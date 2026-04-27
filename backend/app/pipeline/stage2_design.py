"""Stage 2: System Design — IntentIR → SystemDesignIR.

Generates the canonical source of truth that all downstream generators derive from.
"""

from __future__ import annotations

import hashlib
import json
import logging

from app.schemas.intent_ir import IntentIR
from app.schemas.system_design_ir import SystemDesignIR
from app.llm.client import get_llm_client, LLMResponse
from app.llm.prompts import PROMPTS
from app.schemas.common import StageMetrics

logger = logging.getLogger(__name__)

# Simple dict-based cache for MVP (hash of IntentIR → SystemDesignIR)
_design_cache: dict[str, SystemDesignIR] = {}


class SystemDesignError(Exception):
    """Raised when system design generation fails."""
    pass


def _intent_hash(intent_ir: IntentIR) -> str:
    """Compute a deterministic hash of an IntentIR for caching."""
    # Normalize by sorting lists and converting to stable JSON
    data = intent_ir.model_dump()
    data.pop("ambiguity_score", None)  # Don't cache on ambiguity
    data.pop("clarifications_needed", None)
    stable = json.dumps(data, sort_keys=True)
    return hashlib.sha256(stable.encode()).hexdigest()


async def generate_system_design(
    intent_ir: IntentIR,
) -> tuple[SystemDesignIR, StageMetrics]:
    """Generate SystemDesignIR from IntentIR.

    Uses caching: same IntentIR hash → same SystemDesignIR (zero LLM calls).

    Args:
        intent_ir: The structured intent from Stage 1.

    Returns:
        Tuple of (SystemDesignIR, StageMetrics).
    """
    # --- Check cache ---
    cache_key = _intent_hash(intent_ir)
    if cache_key in _design_cache:
        logger.info(f"Stage 2 cache hit for hash {cache_key[:12]}")
        return _design_cache[cache_key], StageMetrics(
            stage="stage2_design",
            latency_ms=0,
            success=True,
        )

    # --- Build prompt ---
    intent_json = json.dumps(intent_ir.model_dump(), indent=2)
    full_prompt = PROMPTS["stage2_design"].replace("{intent_ir}", intent_json)

    # --- Call LLM ---
    client = get_llm_client()
    response: LLMResponse = await client.generate(
        prompt=full_prompt,
        stage="stage2_design",
    )

    if response.parsed is None:
        raise SystemDesignError(
            f"Failed to parse LLM response. Raw: {response.content[:500]}"
        )

    # --- Parse into SystemDesignIR ---
    try:
        design_ir = SystemDesignIR.model_validate(response.parsed)
    except Exception as e:
        raise SystemDesignError(f"SystemDesignIR validation failed: {e}")

    # --- Cache result ---
    _design_cache[cache_key] = design_ir

    metrics = StageMetrics(
        stage="stage2_design",
        latency_ms=response.latency_ms,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        success=True,
    )

    logger.info(
        f"Stage 2 complete: {len(design_ir.entities)} entities, "
        f"{len(design_ir.flows)} flows"
    )

    return design_ir, metrics
