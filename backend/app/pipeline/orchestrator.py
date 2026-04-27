"""Pipeline orchestrator – DAG controller for the 5-stage compiler pipeline.

Stage flow:
    1. Intent Extraction   (NL → IntentIR)          [sequential]
    2. System Design       (IntentIR → SystemDesignIR) [sequential]
    3. Parallel Generation (SystemDesignIR → 4 schemas) [parallel]
    4. Validation + Repair (cross-layer consistency)  [loop, max 3]
    5. Execution Packager  (bootability validation)   [sequential]
"""

from __future__ import annotations

import json
import time
import uuid
import logging
from typing import Any

from app.core.config import settings
from app.schemas.app_config import (
    CompileResponse,
    ValidatedAppConfig,
    MetadataSection,
    DomainSection,
    DomainEntity,
    LogicSection,
)
from app.schemas.common import StageMetrics, PipelineMetrics
from app.pipeline.stage1_intent import extract_intent, IntentExtractionError
from app.pipeline.stage2_design import generate_system_design, SystemDesignError
from app.pipeline.stage3_generators import generate_all_schemas, SchemaGenerationError
from app.pipeline.stage4_validator import validate_app_config
from app.pipeline.stage4_repair import run_repair_loop
from app.pipeline.stage5_packager import generate_execution_report

logger = logging.getLogger(__name__)


def _build_domain_from_design(design_ir_dict: dict) -> DomainSection:
    """Build a DomainSection from SystemDesignIR entities."""
    entities = []
    for name, entity_data in design_ir_dict.get("entities", {}).items():
        fields = []
        field_types = entity_data.get("field_types", {})
        for field_name in entity_data.get("fields", []):
            fields.append({
                "name": field_name,
                "type": field_types.get(field_name, "string"),
                "required": True,
                "unique": field_name in ("email",),
            })
        entities.append(DomainEntity(name=name, fields=fields))
    return DomainSection(entities=entities)


async def _llm_repair_fn(
    layer: str,
    schema_dict: dict,
    errors: list[str],
    full_config: dict,
) -> dict | None:
    """LLM-based repair function for the repair loop."""
    from app.llm.client import get_llm_client
    from app.llm.prompts import PROMPTS

    prompt = (
        PROMPTS["stage4_repair"]
        .replace("{layer}", layer)
        .replace("{current_schema}", json.dumps(schema_dict, indent=2))
        .replace("{errors}", json.dumps(errors, indent=2))
        .replace("{full_config}", json.dumps(full_config, indent=2))
    )

    client = get_llm_client()
    response = await client.generate(prompt=prompt, stage="stage4_repair")

    if response.parsed:
        return response.parsed
    return None


async def run_pipeline(prompt: str) -> CompileResponse:
    """Execute the full 5-stage compiler pipeline.

    Returns a CompileResponse with all results, metrics, and any errors.
    """
    job_id = str(uuid.uuid4())
    start_time = time.time()
    all_metrics: list[StageMetrics] = []
    assumptions: list[str] = []

    logger.info(f"Pipeline started: job_id={job_id}, prompt_length={len(prompt)}")

    try:
        # ============================================================
        # Stage 1: Intent Extraction
        # ============================================================
        logger.info("Stage 1: Intent Extraction")
        intent_ir, s1_metrics = await extract_intent(prompt)
        all_metrics.append(s1_metrics)
        assumptions.extend(intent_ir.assumptions)

        # Check ambiguity gate
        if intent_ir.ambiguity_score > settings.AMBIGUITY_THRESHOLD:
            elapsed = int((time.time() - start_time) * 1000)
            return CompileResponse(
                job_id=job_id,
                status="clarification_needed",
                intent_ir=intent_ir.model_dump(),
                clarifications_needed=intent_ir.clarifications_needed,
                metrics={
                    "latency_ms": elapsed,
                    "ambiguity_score": intent_ir.ambiguity_score,
                    "stage": "stage1_intent",
                },
            )

        # ============================================================
        # Stage 2: System Design
        # ============================================================
        logger.info("Stage 2: System Design")
        design_ir, s2_metrics = await generate_system_design(intent_ir)
        all_metrics.append(s2_metrics)
        assumptions.extend(design_ir.assumptions)

        # ============================================================
        # Stage 3: Parallel Schema Generation
        # ============================================================
        logger.info("Stage 3: Parallel Schema Generation")
        raw_bundle = await generate_all_schemas(design_ir)
        all_metrics.extend(raw_bundle.metrics)

        # ============================================================
        # Assemble AppConfig
        # ============================================================
        domain = _build_domain_from_design(design_ir.model_dump())

        app_config_dict = {
            "metadata": {
                "app_name": intent_ir.app_name,
                "version": "1.0.0",
                "assumptions": assumptions,
            },
            "domain": domain.model_dump(),
            "db": raw_bundle.db,
            "api": raw_bundle.api,
            "ui": raw_bundle.ui,
            "auth": raw_bundle.auth,
            "logic": {"rules": []},
        }

        # ============================================================
        # Stage 4: Validation + Repair
        # ============================================================
        logger.info("Stage 4: Validation + Repair")
        s4_start = time.time()

        repaired_config, repair_report = await run_repair_loop(
            app_config=app_config_dict,
            llm_repair_fn=_llm_repair_fn,
            max_passes=settings.MAX_REPAIR_PASSES,
        )

        s4_latency = int((time.time() - s4_start) * 1000)
        all_metrics.append(StageMetrics(
            stage="stage4_validation",
            latency_ms=s4_latency,
            success=repair_report.final_valid,
        ))

        # ============================================================
        # Stage 5: Execution Packager
        # ============================================================
        logger.info("Stage 5: Execution Packager")
        s5_start = time.time()

        # Try to parse the repaired config
        try:
            validated_config = ValidatedAppConfig.model_validate(repaired_config)
            execution_report = generate_execution_report(validated_config)
        except Exception as e:
            logger.error(f"Stage 5 failed to parse config: {e}")
            execution_report = None
            validated_config = None

        s5_latency = int((time.time() - s5_start) * 1000)
        all_metrics.append(StageMetrics(
            stage="stage5_packager",
            latency_ms=s5_latency,
            success=execution_report is not None and execution_report.overall_pass,
        ))

        # ============================================================
        # Build response
        # ============================================================
        total_latency = int((time.time() - start_time) * 1000)
        total_cost = sum(m.cost_usd for m in all_metrics)

        # Determine status
        if validated_config and execution_report and execution_report.overall_pass:
            status = "success"
        elif validated_config:
            status = "partial"
        else:
            status = "failed"

        pipeline_metrics = PipelineMetrics(
            total_latency_ms=total_latency,
            total_cost_usd=round(total_cost, 4),
            repair_count=repair_report.total_passes,
            consistency_score=round(
                1.0 - (len([a for a in repair_report.actions if not a.success]) / max(len(repair_report.actions), 1)),
                2,
            ) if repair_report.actions else 1.0,
            assumption_count=len(assumptions),
            stages=all_metrics,
        )

        logger.info(
            f"Pipeline complete: status={status}, latency={total_latency}ms, "
            f"repairs={repair_report.total_passes}, cost=${total_cost:.4f}"
        )

        return CompileResponse(
            job_id=job_id,
            status=status,
            app_config=validated_config,
            execution_report=execution_report,
            intent_ir=intent_ir.model_dump(),
            system_design_ir=design_ir.model_dump(),
            validation_errors=[v.model_dump() for v in repair_report.actions[0].errors_before] if repair_report.actions else [],
            repair_log=[a.model_dump() for a in repair_report.actions],
            metrics=pipeline_metrics.model_dump(),
        )

    except (IntentExtractionError, SystemDesignError, SchemaGenerationError) as e:
        elapsed = int((time.time() - start_time) * 1000)
        logger.error(f"Pipeline failed: {e}")
        return CompileResponse(
            job_id=job_id,
            status="failed",
            metrics={"latency_ms": elapsed, "error": str(e)},
        )
    except Exception as e:
        elapsed = int((time.time() - start_time) * 1000)
        logger.error(f"Pipeline unexpected error: {e}", exc_info=True)
        return CompileResponse(
            job_id=job_id,
            status="failed",
            metrics={"latency_ms": elapsed, "error": str(e)},
        )
