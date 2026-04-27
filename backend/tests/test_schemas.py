"""Tests for Pydantic schema models."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.intent_ir import IntentIR
from app.schemas.system_design_ir import SystemDesignIR, EntityDesign
from app.schemas.db_schema import DBSchema, DBTable, DBColumn
from app.schemas.api_schema import APISchema, APIResource, APIEndpoint
from app.schemas.ui_schema import UISchema, UIPage, UIComponent
from app.schemas.auth_schema import AuthSchema
from app.schemas.app_config import ValidatedAppConfig

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestIntentIR:
    def test_valid_minimal(self):
        ir = IntentIR(app_name="CRM", features=["login"], entities=["User"])
        assert ir.app_name == "CRM"
        assert ir.ambiguity_score == 0.0

    def test_valid_full(self):
        ir = IntentIR(
            app_name="CRM Pro",
            features=["login", "dashboard", "contacts"],
            entities=["User", "Contact"],
            roles=["user", "admin"],
            premium_features=["analytics"],
            payment_provider="stripe",
            ambiguity_score=0.3,
            assumptions=["Default 2 roles"],
        )
        assert ir.payment_provider == "stripe"
        assert len(ir.assumptions) == 1

    def test_ambiguity_score_bounds(self):
        with pytest.raises(ValidationError):
            IntentIR(app_name="X", features=[], entities=[], ambiguity_score=1.5)

        with pytest.raises(ValidationError):
            IntentIR(app_name="X", features=[], entities=[], ambiguity_score=-0.1)


class TestSystemDesignIR:
    def test_valid(self):
        design = SystemDesignIR(
            app_name="CRM",
            entities={
                "User": EntityDesign(
                    name="User",
                    fields=["email", "password", "name"],
                    relations=["has_many:Contact"],
                )
            },
            flows={"auth_flow": ["register", "login", "jwt_issue"]},
            access_control_matrix={"admin": ["*"], "user": ["contacts.*"]},
        )
        assert "User" in design.entities
        assert len(design.flows["auth_flow"]) == 3


class TestDBSchema:
    def test_valid_table(self):
        schema = DBSchema(
            tables=[
                DBTable(
                    name="users",
                    entity="User",
                    columns=[
                        DBColumn(name="id", type="UUID", primary_key=True),
                        DBColumn(name="email", type="VARCHAR", unique=True),
                    ],
                )
            ]
        )
        assert len(schema.tables) == 1
        assert schema.tables[0].columns[0].primary_key is True


class TestAPISchema:
    def test_valid_resource(self):
        schema = APISchema(
            resources=[
                APIResource(
                    name="contacts",
                    entity="Contact",
                    base_path="/api/contacts",
                    endpoints=[
                        APIEndpoint(method="GET", path="/api/contacts"),
                        APIEndpoint(method="POST", path="/api/contacts"),
                    ],
                )
            ]
        )
        assert len(schema.resources[0].endpoints) == 2


class TestAuthSchema:
    def test_defaults(self):
        auth = AuthSchema()
        assert auth.strategy == "jwt"
        assert auth.password_storage == "bcrypt"
        assert auth.token_expiry == "24h"
        assert auth.rate_limit_enabled is True

    def test_cannot_override_password_storage(self):
        """password_storage is Literal['bcrypt'] — cannot be set to anything else."""
        with pytest.raises(ValidationError):
            AuthSchema(password_storage="plaintext")


class TestValidatedAppConfig:
    def test_load_valid_fixture(self):
        fixture_path = FIXTURES_DIR / "valid_appconfig_crm.json"
        with open(fixture_path) as f:
            data = json.load(f)
        config = ValidatedAppConfig.model_validate(data)
        assert config.metadata.app_name == "CRM Pro"
        assert len(config.domain.entities) == 3
        assert len(config.db.tables) == 3
        assert len(config.api.resources) == 4
        assert len(config.ui.pages) == 5
        assert config.auth.strategy == "jwt"
        assert config.auth.password_storage == "bcrypt"
