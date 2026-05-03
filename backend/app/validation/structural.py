"""Per-layer structural validation against Pydantic models.

Validates that each schema layer (db, api, ui, auth) independently
conforms to its Pydantic model structure.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from app.schemas.common import ValidationViolation, Severity
from app.schemas.db_schema import DBSchema
from app.schemas.api_schema import APISchema
from app.schemas.ui_schema import UISchema
from app.schemas.auth_schema import AuthSchema
from app.schemas.app_config import (
    ValidatedAppConfig,
    MetadataSection,
    DomainSection,
    LogicSection,
)


import logging

logger = logging.getLogger(__name__)


# Map of layer name → Pydantic model class
LAYER_MODELS: dict[str, type] = {
    "metadata": MetadataSection,
    "domain": DomainSection,
    "db": DBSchema,
    "api": APISchema,
    "ui": UISchema,
    "auth": AuthSchema,
    "logic": LogicSection,
}


def validate_structure(app_config: dict[str, Any]) -> list[ValidationViolation]:
    """Validate each layer of an AppConfig dict against its Pydantic model.

    Returns a list of structural validation violations.
    """
    violations: list[ValidationViolation] = []

    for layer_name, model_cls in LAYER_MODELS.items():
        layer_data = app_config.get(layer_name)

        if layer_data is None:
            violations.append(
                ValidationViolation(
                    rule_id=f"STRUCT-{layer_name.upper()}-MISSING",
                    layer=layer_name,
                    message=f"Required layer '{layer_name}' is missing from AppConfig",
                    severity=Severity.ERROR,
                    fix_hint=f"Add a '{layer_name}' section to the AppConfig",
                )
            )
            continue

        try:
            model_cls.model_validate(layer_data)
        except PydanticValidationError as e:
            logger.error(f"Structural validation failed for layer {layer_name}: {e}", exc_info=True)
            for err in e.errors():
                field_path = ".".join(str(loc) for loc in err["loc"])
                violations.append(
                    ValidationViolation(
                        rule_id=f"STRUCT-{layer_name.upper()}-INVALID",
                        layer=layer_name,
                        message=f"{layer_name}.{field_path}: {err['msg']}",
                        severity=Severity.ERROR,
                        fix_hint=f"Fix field '{field_path}' in layer '{layer_name}'",
                        field_path=f"{layer_name}.{field_path}",
                    )
                )

    return violations


def validate_full_config(app_config: dict[str, Any]) -> tuple[ValidatedAppConfig | None, list[ValidationViolation]]:
    """Try to parse the entire AppConfig. Returns (parsed_config, violations).

    If parsing succeeds, returns (config, []). Otherwise returns (None, violations).
    """
    try:
        config = ValidatedAppConfig.model_validate(app_config)
        return config, []
    except PydanticValidationError as e:
        logger.error(f"Full config validation failed: {e}", exc_info=True)
        violations = []
        for err in e.errors():
            field_path = ".".join(str(loc) for loc in err["loc"])
            layer = str(err["loc"][0]) if err["loc"] else "unknown"
            violations.append(
                ValidationViolation(
                    rule_id="STRUCT-FULL-INVALID",
                    layer=layer,
                    message=f"{field_path}: {err['msg']}",
                    severity=Severity.ERROR,
                    field_path=field_path,
                )
            )
        return None, violations
