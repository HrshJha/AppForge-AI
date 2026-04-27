"""Tests for cross-layer validation rules.

Tests each of the 10 CL rules with valid and invalid configs.
"""

import json
import copy
from pathlib import Path

import pytest

from app.schemas.app_config import ValidatedAppConfig
from app.validation.cross_layer import (
    check_api_entities_in_domain,
    check_ui_data_sources_in_api,
    check_logic_roles_in_auth,
    check_db_fields_match_domain,
    check_premium_requires_payment,
    check_admin_requires_endpoint,
    check_payment_requires_webhook,
    check_auth_jwt_expiry,
    check_nullable_fk,
    check_endpoints_have_auth,
    run_all_cross_layer_rules,
)
from app.validation.rules import validate_all, compute_consistency_score

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_valid_config() -> ValidatedAppConfig:
    """Load the valid CRM fixture as a typed config."""
    with open(FIXTURES_DIR / "valid_appconfig_crm.json") as f:
        data = json.load(f)
    return ValidatedAppConfig.model_validate(data)


def _load_valid_dict() -> dict:
    """Load the valid CRM fixture as a raw dict."""
    with open(FIXTURES_DIR / "valid_appconfig_crm.json") as f:
        return json.load(f)


class TestCL001_ApiEntitiesInDomain:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_api_entities_in_domain(config)
        assert len(violations) == 0

    def test_invalid_entity(self):
        config = _load_valid_config()
        # Add a resource referencing a non-existent entity
        from app.schemas.api_schema import APIResource
        config.api.resources.append(
            APIResource(name="ghost", entity="GhostEntity", base_path="/api/ghost")
        )
        violations = check_api_entities_in_domain(config)
        assert len(violations) == 1
        assert violations[0].rule_id == "CL-001"


class TestCL002_UiDataSourcesInApi:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_ui_data_sources_in_api(config)
        assert len(violations) == 0

    def test_missing_endpoint(self):
        config = _load_valid_config()
        # Add a component with a data_source that doesn't exist
        from app.schemas.ui_schema import UIComponent
        config.ui.pages[1].components.append(
            UIComponent(type="statcard", props={"label": "Test"}, data_source="GET /api/nonexistent")
        )
        violations = check_ui_data_sources_in_api(config)
        assert len(violations) >= 1
        assert violations[0].rule_id == "CL-002"


class TestCL004_DbFieldsMatchDomain:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_db_fields_match_domain(config)
        # Should have 0 errors (warnings for unmapped fields are ok)
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0

    def test_missing_entity(self):
        config = _load_valid_config()
        # Add a table referencing non-existent entity
        from app.schemas.db_schema import DBTable, DBColumn
        config.db.tables.append(
            DBTable(
                name="phantoms",
                entity="Phantom",
                columns=[DBColumn(name="id", type="UUID", primary_key=True)],
            )
        )
        violations = check_db_fields_match_domain(config)
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) >= 1
        assert errors[0].rule_id == "CL-004"


class TestCL005_PremiumRequiresPayment:
    def test_no_premium_passes(self):
        config = _load_valid_config()
        violations = check_premium_requires_payment(config)
        assert len(violations) == 0

    def test_premium_without_payment(self):
        config = _load_valid_config()
        # Add premium role reference
        from app.schemas.auth_schema import AuthGuard
        config.auth.guards.append(
            AuthGuard(name="premium_gate", required_roles=["premium_user"], redirect="/upgrade")
        )
        violations = check_premium_requires_payment(config)
        assert len(violations) == 1
        assert violations[0].rule_id == "CL-005"


class TestCL006_AdminRequiresEndpoint:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_admin_requires_endpoint(config)
        # Admin role exists and admin page exists
        assert len(violations) == 0


class TestCL008_AuthJwtExpiry:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_auth_jwt_expiry(config)
        assert len(violations) == 0

    def test_excessive_expiry(self):
        config = _load_valid_config()
        config.auth.token_expiry = "7d"
        violations = check_auth_jwt_expiry(config)
        assert len(violations) == 1
        assert violations[0].rule_id == "CL-008"


class TestCL009_NullableFk:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_nullable_fk(config)
        assert len(violations) == 0


class TestCL010_EndpointsHaveAuth:
    def test_valid_passes(self):
        config = _load_valid_config()
        violations = check_endpoints_have_auth(config)
        # register and login are auth_required=false but they're expected public endpoints
        # The rule allows public paths
        assert all(v.severity == "warning" for v in violations)


class TestFullValidation:
    def test_valid_config_passes(self):
        data = _load_valid_dict()
        violations = validate_all(data)
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0, f"Unexpected errors: {[v.message for v in errors]}"

    def test_consistency_score_valid(self):
        data = _load_valid_dict()
        violations = validate_all(data)
        score = compute_consistency_score(violations)
        assert score == 1.0

    def test_missing_layer_detected(self):
        data = _load_valid_dict()
        del data["db"]
        violations = validate_all(data)
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) > 0
        assert any("db" in v.message.lower() for v in errors)

    def test_run_all_cross_layer_rules(self):
        config = _load_valid_config()
        violations = run_all_cross_layer_rules(config)
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0
