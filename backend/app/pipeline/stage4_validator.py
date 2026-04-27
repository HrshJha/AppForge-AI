"""Stage 4 Validator — three-pass validation engine.

Runs JSON syntax repair → structural validation → cross-layer consistency
and returns a comprehensive ValidationReport.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ValidationViolation, Severity
from app.schemas.app_config import ValidatedAppConfig
from app.validation.json_repair import repair_json
from app.validation.rules import validate_all, compute_consistency_score


class ValidationReport(BaseModel):
    """Report produced by the Stage 4 validator."""
    valid: bool = False
    consistency_score: float = 0.0
    violations: list[ValidationViolation] = Field(default_factory=list)
    json_was_repaired: bool = False
    structural_pass: bool = False
    cross_layer_pass: bool = False


def validate_app_config(
    raw_config: dict | str,
) -> tuple[dict | None, ValidationReport]:
    """Run three-pass validation on an AppConfig.

    Args:
        raw_config: Either a dict (already parsed) or a raw JSON string.

    Returns:
        Tuple of (repaired_config_dict, validation_report).
        repaired_config_dict is None if validation failed completely.
    """
    report = ValidationReport()

    # --- Pass 0: JSON repair (if string input) ---
    if isinstance(raw_config, str):
        try:
            config_dict, was_repaired = repair_json(raw_config)
            report.json_was_repaired = was_repaired
        except ValueError as e:
            report.violations.append(
                ValidationViolation(
                    rule_id="JSON-REPAIR-FAIL",
                    layer="json",
                    message=f"JSON repair failed: {str(e)}",
                    severity=Severity.ERROR,
                )
            )
            return None, report
    else:
        config_dict = raw_config

    # --- Pass 1 + 2: Structural + Cross-layer ---
    violations = validate_all(config_dict)
    report.violations = violations

    # Determine pass status
    error_violations = [v for v in violations if v.severity == Severity.ERROR]
    structural_errors = [v for v in error_violations if v.rule_id.startswith("STRUCT")]
    cross_layer_errors = [v for v in error_violations if v.rule_id.startswith("CL-")]

    report.structural_pass = len(structural_errors) == 0
    report.cross_layer_pass = len(cross_layer_errors) == 0
    report.valid = len(error_violations) == 0
    report.consistency_score = compute_consistency_score(violations)

    return config_dict, report
