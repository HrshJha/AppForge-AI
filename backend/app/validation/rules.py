"""Validation rules registry — orchestrates all validation passes.

Three-pass validation:
    1. JSON syntax repair (pre-parse)
    2. Structural validation (per-layer Pydantic)
    3. Cross-layer consistency rules
"""

from __future__ import annotations

from typing import Any

from app.schemas.common import ValidationViolation, Severity
from app.schemas.app_config import ValidatedAppConfig
from app.validation.structural import validate_structure, validate_full_config
from app.validation.cross_layer import run_all_cross_layer_rules


def validate_all(app_config: dict[str, Any]) -> list[ValidationViolation]:
    """Run all validation passes against an AppConfig dict.

    Pass 1: Structural validation (Pydantic model conformance)
    Pass 2: Cross-layer consistency rules (if structural passes)

    Returns a list of all violations found.
    """
    violations: list[ValidationViolation] = []

    # --- Pass 1: Structural validation ---
    structural_violations = validate_structure(app_config)
    violations.extend(structural_violations)

    # If there are structural errors, we can't run cross-layer rules
    structural_errors = [v for v in structural_violations if v.severity == Severity.ERROR]
    if structural_errors:
        return violations

    # --- Pass 2: Parse into typed config ---
    config, parse_violations = validate_full_config(app_config)
    if parse_violations:
        violations.extend(parse_violations)
        return violations

    if config is None:
        return violations

    # --- Pass 3: Cross-layer consistency ---
    cross_layer_violations = run_all_cross_layer_rules(config)
    violations.extend(cross_layer_violations)

    return violations


def compute_consistency_score(violations: list[ValidationViolation]) -> float:
    """Compute consistency score as percentage of rules passing.

    Score = (total_rules - error_count) / total_rules
    """
    total_rules = 10  # CL-001 through CL-010
    error_count = len([v for v in violations if v.severity == Severity.ERROR and v.rule_id.startswith("CL-")])
    return max(0.0, (total_rules - error_count) / total_rules) if total_rules > 0 else 0.0
