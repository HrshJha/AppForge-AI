"""Stage 3: Parallel Schema Generators.

Four generators run concurrently via asyncio.gather():
    1. DB Schema Generator
    2. API Schema Generator
    3. UI Schema Generator
    4. Auth Schema Generator

All derive from SystemDesignIR — never from each other.
"""

from __future__ import annotations

import asyncio
import json
import logging

from app.schemas.system_design_ir import SystemDesignIR
from app.schemas.db_schema import DBSchema
from app.schemas.api_schema import APISchema
from app.schemas.ui_schema import UISchema
from app.schemas.auth_schema import AuthSchema
from app.schemas.common import StageMetrics
from app.llm.client import get_llm_client, LLMResponse
from app.llm.prompts import PROMPTS

logger = logging.getLogger(__name__)


class SchemaGenerationError(Exception):
    """Raised when a schema generator fails."""
    def __init__(self, layer: str, message: str):
        self.layer = layer
        super().__init__(f"[{layer}] {message}")


class RawSchemaBundle:
    """Container for all 4 generated schemas (pre-validation)."""

    def __init__(
        self,
        db: dict,
        api: dict,
        ui: dict,
        auth: dict,
        metrics: list[StageMetrics],
    ):
        self.db = db
        self.api = api
        self.ui = ui
        self.auth = auth
        self.metrics = metrics


async def _generate_layer(
    stage_key: str,
    system_design_ir: SystemDesignIR,
) -> tuple[dict, StageMetrics]:
    """Generate a single schema layer from SystemDesignIR."""
    design_json = json.dumps(system_design_ir.model_dump(), indent=2)
    full_prompt = PROMPTS[stage_key].replace("{system_design_ir}", design_json)

    client = get_llm_client()
    response: LLMResponse = await client.generate(
        prompt=full_prompt,
        stage=stage_key,
    )

    if response.parsed is None:
        raise SchemaGenerationError(
            stage_key,
            f"Failed to parse response. Raw: {response.content[:300]}",
        )

    metrics = StageMetrics(
        stage=stage_key,
        latency_ms=response.latency_ms,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        success=True,
    )

    return response.parsed, metrics


async def generate_all_schemas(
    system_design_ir: SystemDesignIR,
) -> RawSchemaBundle:
    """Run all 4 schema generators sequentially with pauses.

    Sequential execution avoids exceeding Groq free-tier TPM limits.

    Args:
        system_design_ir: The canonical source of truth from Stage 2.

    Returns:
        RawSchemaBundle containing all 4 generated schemas (unvalidated).
    """
    logger.info("Stage 3: Running 4 schema generators sequentially...")

    schemas: dict[str, dict] = {}
    metrics: list[StageMetrics] = []
    stage_keys = [
        ("db", "stage3_db"),
        ("api", "stage3_api"),
        ("ui", "stage3_ui"),
        ("auth", "stage3_auth"),
    ]

    for i, (layer, stage_key) in enumerate(stage_keys):
        try:
            schema_dict, stage_metrics = await _generate_layer(stage_key, system_design_ir)
            schemas[layer] = schema_dict
            metrics.append(stage_metrics)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Stage 3 {layer} generator failed: {e}", exc_info=True)
            raise SchemaGenerationError(layer, str(e)) from e

        # Pause between calls to stay within Groq TPM window
        if i < len(stage_keys) - 1:
            await asyncio.sleep(2)

    logger.info(
        f"Stage 3 complete: "
        f"{sum(1 for m in metrics if m.success)}/4 generators succeeded"
    )

    return RawSchemaBundle(
        db=schemas["db"],
        api=schemas["api"],
        ui=schemas["ui"],
        auth=schemas["auth"],
        metrics=metrics,
    )
