"""Stage 4 Repair Engine — surgical per-layer repair with oscillation detection.

Key principles:
    - Only re-generate the failing layer, not the full pipeline
    - Inject error context so the LLM knows what to fix
    - Max 3 repair passes per layer
    - Detect oscillation (same errors repeating) and escalate
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ValidationViolation
from app.pipeline.stage4_validator import validate_app_config, ValidationReport


class OscillationError(Exception):
    """Raised when repair oscillation is detected."""
    def __init__(self, layer: str, errors: list[str]):
        self.layer = layer
        self.errors = errors
        super().__init__(
            f"Repair oscillation detected on layer '{layer}': "
            f"errors are cycling. Escalating. Errors: {errors}"
        )


class RepairAction(BaseModel):
    """Record of a single repair action taken."""
    layer: str
    pass_number: int
    errors_before: list[str] = Field(default_factory=list)
    errors_after: list[str] = Field(default_factory=list)
    success: bool = False
    oscillation_detected: bool = False


class RepairReport(BaseModel):
    """Full report of the repair process."""
    total_passes: int = 0
    layers_repaired: list[str] = Field(default_factory=list)
    actions: list[RepairAction] = Field(default_factory=list)
    final_valid: bool = False
    oscillation_detected: bool = False
    escalated: bool = False


def _error_hash(errors: list[str]) -> str:
    """Compute a deterministic hash of a sorted error list for oscillation detection."""
    return hashlib.md5(json.dumps(sorted(errors)).encode()).hexdigest()


def _group_violations_by_layer(
    violations: list[ValidationViolation],
) -> dict[str, list[ValidationViolation]]:
    """Group violations by their layer field."""
    groups: dict[str, list[ValidationViolation]] = {}
    for v in violations:
        layer = v.layer
        if layer not in groups:
            groups[layer] = []
        groups[layer].append(v)
    return groups


async def run_repair_loop(
    app_config: dict[str, Any],
    llm_repair_fn: Any = None,
    max_passes: int = 3,
) -> tuple[dict[str, Any], RepairReport]:
    """Run the surgical repair loop.

    Args:
        app_config: The current AppConfig dict to repair.
        llm_repair_fn: Async function(layer, schema_dict, errors) -> repaired_dict.
                       If None, repair is skipped (useful for testing).
        max_passes: Maximum repair passes per layer.

    Returns:
        Tuple of (repaired_config, repair_report).
    """
    report = RepairReport()
    current_config = app_config.copy()

    # Track error hashes per layer for oscillation detection
    error_hash_history: dict[str, list[str]] = {}  # layer -> list of error hashes

    for pass_num in range(1, max_passes + 1):
        # Validate current config
        _, validation_report = validate_app_config(current_config)

        if validation_report.valid:
            report.final_valid = True
            break

        # Group errors by layer
        error_violations = [
            v for v in validation_report.violations if v.severity == "error"
        ]
        if not error_violations:
            report.final_valid = True
            break

        layer_groups = _group_violations_by_layer(error_violations)
        report.total_passes = pass_num

        for layer, violations in layer_groups.items():
            error_messages = [v.message for v in violations]

            # --- Oscillation detection ---
            h = _error_hash(error_messages)
            if layer not in error_hash_history:
                error_hash_history[layer] = []

            if h in error_hash_history[layer]:
                # Oscillation detected!
                action = RepairAction(
                    layer=layer,
                    pass_number=pass_num,
                    errors_before=error_messages,
                    oscillation_detected=True,
                )
                report.actions.append(action)
                report.oscillation_detected = True
                report.escalated = True
                continue

            error_hash_history[layer].append(h)

            # --- Surgical repair ---
            action = RepairAction(
                layer=layer,
                pass_number=pass_num,
                errors_before=error_messages,
            )

            if llm_repair_fn is not None:
                try:
                    layer_data = current_config.get(layer, {})
                    repaired_layer = await llm_repair_fn(
                        layer=layer,
                        schema_dict=layer_data,
                        errors=error_messages,
                        full_config=current_config,
                    )
                    if repaired_layer:
                        current_config[layer] = repaired_layer
                        if layer not in report.layers_repaired:
                            report.layers_repaired.append(layer)
                        action.success = True
                except Exception as e:
                    action.errors_after = [str(e)]
            else:
                # No LLM function — can't repair
                action.errors_after = error_messages

            report.actions.append(action)

    # Final validation
    _, final_report = validate_app_config(current_config)
    report.final_valid = final_report.valid

    return current_config, report
