"""Stage 5: Execution Packager — validation-only bootability checks.

MVP scope: No file generation. Instead, validates that the AppConfig
CAN boot by checking:
    1. DB bootability — all field types are valid SQL types
    2. API completeness — all endpoints have handler mappings
    3. UI renderability — all component types have renderer mappings
    4. Auth sanity — JWT config is properly set
"""

from __future__ import annotations

import logging

from app.schemas.app_config import ValidatedAppConfig, ExecutionCheck, ExecutionReport

logger = logging.getLogger(__name__)

# Valid SQL types that map to real database types
VALID_SQL_TYPES = {
    "VARCHAR", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP",
    "TEXT", "JSONB", "UUID", "BIGINT", "SERIAL", "NUMERIC",
    "DATE", "DATETIME", "REAL", "BLOB",
}

# Valid UI component types that have renderer mappings
VALID_COMPONENT_TYPES = {
    "table", "form", "statcard", "heading", "button", "chart", "list",
}

# Valid HTTP methods
VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def check_db_bootability(config: ValidatedAppConfig) -> ExecutionCheck:
    """Check that all DB column types are valid SQL types."""
    errors = []

    for table in config.db.tables:
        if not table.columns:
            errors.append(f"Table '{table.name}' has no columns")
            continue

        has_pk = False
        for col in table.columns:
            if col.type.upper() not in VALID_SQL_TYPES:
                errors.append(
                    f"Table '{table.name}' column '{col.name}' has invalid SQL type '{col.type}'"
                )
            if col.primary_key:
                has_pk = True

        if not has_pk:
            errors.append(f"Table '{table.name}' has no primary key")

    return ExecutionCheck(
        name="db_bootability",
        passed=len(errors) == 0,
        details=f"Checked {len(config.db.tables)} tables",
        errors=errors,
    )


def check_api_completeness(config: ValidatedAppConfig) -> ExecutionCheck:
    """Check that all API endpoints have valid method + path mappings."""
    errors = []

    for resource in config.api.resources:
        if not resource.endpoints:
            errors.append(f"Resource '{resource.name}' has no endpoints")
            continue

        for endpoint in resource.endpoints:
            if endpoint.method.value not in VALID_METHODS:
                errors.append(
                    f"Endpoint {endpoint.path} has invalid method '{endpoint.method}'"
                )
            if not endpoint.path.startswith("/"):
                errors.append(
                    f"Endpoint path '{endpoint.path}' must start with '/'"
                )

    total_endpoints = sum(len(r.endpoints) for r in config.api.resources)
    return ExecutionCheck(
        name="api_completeness",
        passed=len(errors) == 0,
        details=f"Checked {total_endpoints} endpoints across {len(config.api.resources)} resources",
        errors=errors,
    )


def check_ui_renderability(config: ValidatedAppConfig) -> ExecutionCheck:
    """Check that all UI component types have renderer mappings."""
    errors = []

    for page in config.ui.pages:
        for i, component in enumerate(page.components):
            if component.type not in VALID_COMPONENT_TYPES:
                errors.append(
                    f"Page '{page.id}' component [{i}] has unknown type '{component.type}' — "
                    f"valid types: {VALID_COMPONENT_TYPES}"
                )

    total_components = sum(len(p.components) for p in config.ui.pages)
    return ExecutionCheck(
        name="ui_renderability",
        passed=len(errors) == 0,
        details=f"Checked {total_components} components across {len(config.ui.pages)} pages",
        errors=errors,
    )


def check_auth_sanity(config: ValidatedAppConfig) -> ExecutionCheck:
    """Check that auth config meets non-negotiable security requirements."""
    errors = []

    if config.auth.strategy != "jwt":
        errors.append(f"Auth strategy must be 'jwt', got '{config.auth.strategy}'")

    if config.auth.password_storage != "bcrypt":
        errors.append(
            f"Password storage must be 'bcrypt', got '{config.auth.password_storage}'"
        )

    if not config.auth.token_expiry:
        errors.append("Auth token_expiry is not set")

    if not config.auth.rate_limit_enabled:
        errors.append("Rate limiting must be enabled")

    if not config.auth.roles:
        errors.append("Auth must define at least one role")

    return ExecutionCheck(
        name="auth_sanity",
        passed=len(errors) == 0,
        details=f"Checked auth config: strategy={config.auth.strategy}, expiry={config.auth.token_expiry}",
        errors=errors,
    )


def generate_execution_report(config: ValidatedAppConfig) -> ExecutionReport:
    """Generate a full execution readiness report.

    No file I/O — just validates the config CAN boot.
    """
    db_check = check_db_bootability(config)
    api_check = check_api_completeness(config)
    ui_check = check_ui_renderability(config)
    auth_check = check_auth_sanity(config)

    overall = all([
        db_check.passed,
        api_check.passed,
        ui_check.passed,
        auth_check.passed,
    ])

    logger.info(
        f"Stage 5 execution report: overall={'PASS' if overall else 'FAIL'} "
        f"(db={db_check.passed}, api={api_check.passed}, "
        f"ui={ui_check.passed}, auth={auth_check.passed})"
    )

    return ExecutionReport(
        db_bootable=db_check,
        api_complete=api_check,
        ui_renderable=ui_check,
        auth_sane=auth_check,
        overall_pass=overall,
    )
