"""Stage 5: Execution Packager — repair-capable bootability checker.

Runs 4 boot-check groups in order, auto-repairs failures, then
cross-checks referential integrity.  Supports up to 3 repair passes
with oscillation detection.

Boot groups:
    1. DB_BOOT   — column types, primary keys, duplicate columns
    2. API_BOOT  — methods, paths, auth_required presence
    3. UI_BOOT   — component types against renderer whitelist
    4. AUTH_BOOT  — JWT strategy, bcrypt, rate-limit, expiry

After repairs, a cross-check validates FK references, API entity
existence, and UI data-source resolution.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.app_config import ValidatedAppConfig, ExecutionCheck, ExecutionReport

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Whitelists
# ---------------------------------------------------------------------------

VALID_SQL_TYPES = {
    "VARCHAR", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP",
    "TEXT", "JSONB", "UUID", "BIGINT", "SERIAL", "NUMERIC",
    "DATE", "DATETIME", "REAL", "BLOB",
}

# Mapping unknown types → nearest valid SQL type
SQL_TYPE_MAP: dict[str, str] = {
    "string": "TEXT",
    "str": "TEXT",
    "text": "TEXT",
    "number": "INTEGER",
    "int": "INTEGER",
    "integer": "INTEGER",
    "bigint": "BIGINT",
    "float": "FLOAT",
    "real": "REAL",
    "double": "FLOAT",
    "decimal": "NUMERIC",
    "numeric": "NUMERIC",
    "bool": "BOOLEAN",
    "boolean": "BOOLEAN",
    "date": "TIMESTAMP",
    "datetime": "TIMESTAMP",
    "timestamp": "TIMESTAMP",
    "time": "TIMESTAMP",
    "id": "UUID",
    "uuid": "UUID",
    "serial": "SERIAL",
    "json": "JSONB",
    "jsonb": "JSONB",
    "blob": "BLOB",
    "binary": "BLOB",
    "email": "VARCHAR",
    "password": "VARCHAR",
    "varchar": "VARCHAR",
    "enum": "VARCHAR",
    "relation": "UUID",
}

VALID_COMPONENT_TYPES = {
    "table", "form", "statcard", "heading", "button", "chart", "list",
    "card", "modal", "input", "select", "datepicker", "fileupload",
    "richtext", "map", "kanbanboard", "calendar",
}

# Semantic similarity map for unknown UI component types
UI_TYPE_MAP: dict[str, str] = {
    "datagrid": "table",
    "grid": "table",
    "data_table": "table",
    "dropdown": "select",
    "textarea": "richtext",
    "text_area": "richtext",
    "picker": "datepicker",
    "date_picker": "datepicker",
    "file_upload": "fileupload",
    "upload": "fileupload",
    "kanban": "kanbanboard",
    "kanban_board": "kanbanboard",
    "rich_text": "richtext",
    "stat": "statcard",
    "stats": "statcard",
    "metric": "statcard",
    "metrics": "statcard",
    "header": "heading",
    "title": "heading",
    "nav": "button",
    "link": "button",
    "dialog": "modal",
    "popup": "modal",
    "graph": "chart",
    "bar_chart": "chart",
    "pie_chart": "chart",
    "line_chart": "chart",
}

VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


# ---------------------------------------------------------------------------
# Boot check result model
# ---------------------------------------------------------------------------

class BootCheckResult(BaseModel):
    """Result of a single boot-check group."""
    name: str
    passed: bool = True
    fixes: list[str] = Field(default_factory=list)
    oscillation_detected: bool = False


class BootRepairReport(BaseModel):
    """Full Stage 5 repair report."""
    db_boot: BootCheckResult = Field(default_factory=lambda: BootCheckResult(name="db_boot"))
    api_boot: BootCheckResult = Field(default_factory=lambda: BootCheckResult(name="api_boot"))
    ui_boot: BootCheckResult = Field(default_factory=lambda: BootCheckResult(name="ui_boot"))
    auth_boot: BootCheckResult = Field(default_factory=lambda: BootCheckResult(name="auth_boot"))
    cross_check: BootCheckResult = Field(default_factory=lambda: BootCheckResult(name="cross_check"))
    total_fixes: int = 0
    oscillation_detected: bool = False


# ---------------------------------------------------------------------------
# DB_BOOT — column types, PKs, duplicate columns
# ---------------------------------------------------------------------------

def _repair_db(config_dict: dict[str, Any]) -> BootCheckResult:
    """Validate and repair DB schema for bootability."""
    result = BootCheckResult(name="db_boot")
    db = config_dict.get("db", {})
    tables = db.get("tables", [])

    for table in tables:
        table_name = table.get("name", "?")
        columns = table.get("columns", [])

        # --- Check / fix column types ---
        for col in columns:
            col_type = col.get("type", "")
            if col_type.upper() not in VALID_SQL_TYPES:
                mapped = SQL_TYPE_MAP.get(col_type.lower(), "TEXT")
                result.fixes.append(
                    f"DB: table '{table_name}' column '{col.get('name', '?')}' "
                    f"type '{col_type}' → '{mapped}'"
                )
                col["type"] = mapped

        # --- Check / fix primary key ---
        has_pk = any(col.get("primary_key", False) for col in columns)
        if not has_pk:
            pk_col = {
                "name": "id",
                "type": "UUID",
                "primary_key": True,
                "nullable": False,
                "unique": True,
            }
            columns.insert(0, pk_col)
            table["columns"] = columns
            result.fixes.append(
                f"DB: table '{table_name}' missing PK → added 'id' UUID column"
            )

        # --- Check / fix duplicate column names ---
        seen_names: dict[str, int] = {}
        for col in columns:
            name = col.get("name", "")
            if name in seen_names:
                seen_names[name] += 1
                new_name = f"{name}_{seen_names[name]}"
                result.fixes.append(
                    f"DB: table '{table_name}' duplicate column '{name}' → renamed to '{new_name}'"
                )
                col["name"] = new_name
            else:
                seen_names[name] = 1

    result.passed = len(result.fixes) == 0
    return result


# ---------------------------------------------------------------------------
# API_BOOT — methods, paths, auth_required
# ---------------------------------------------------------------------------

def _repair_api(config_dict: dict[str, Any]) -> BootCheckResult:
    """Validate and repair API schema for bootability."""
    result = BootCheckResult(name="api_boot")
    api = config_dict.get("api", {})
    resources = api.get("resources", [])

    for resource in resources:
        endpoints = resource.get("endpoints", [])
        for ep in endpoints:
            # --- Check / fix method ---
            method = ep.get("method", "").upper()
            if method not in VALID_METHODS:
                path = ep.get("path", "").lower()
                if "create" in path or "register" in path or "login" in path:
                    inferred = "POST"
                elif "delete" in path or "remove" in path:
                    inferred = "DELETE"
                elif "update" in path or "edit" in path:
                    inferred = "PUT"
                elif "list" in path or "get" in path or "search" in path:
                    inferred = "GET"
                else:
                    inferred = "POST"
                result.fixes.append(
                    f"API: endpoint '{ep.get('path', '?')}' invalid method '{method}' → '{inferred}'"
                )
                ep["method"] = inferred

            # --- Check / fix path prefix ---
            path = ep.get("path", "")
            if path and not path.startswith("/"):
                ep["path"] = "/" + path
                result.fixes.append(
                    f"API: endpoint path '{path}' missing '/' prefix → '/{path}'"
                )

            # --- Check / fix auth_required ---
            if "auth_required" not in ep:
                ep["auth_required"] = True
                result.fixes.append(
                    f"API: endpoint '{ep.get('method', '?')} {ep.get('path', '?')}' "
                    f"missing auth_required → set to true"
                )

    result.passed = len(result.fixes) == 0
    return result


# ---------------------------------------------------------------------------
# UI_BOOT — component types against whitelist
# ---------------------------------------------------------------------------

def _repair_ui(config_dict: dict[str, Any]) -> BootCheckResult:
    """Validate and repair UI schema for bootability."""
    result = BootCheckResult(name="ui_boot")
    ui = config_dict.get("ui", {})
    pages = ui.get("pages", [])

    for page in pages:
        page_id = page.get("id", "?")
        components = page.get("components", [])
        for i, comp in enumerate(components):
            comp_type = comp.get("type", "")
            if comp_type.lower() not in VALID_COMPONENT_TYPES:
                mapped = UI_TYPE_MAP.get(comp_type.lower(), "card")
                result.fixes.append(
                    f"UI: page '{page_id}' component [{i}] unknown type "
                    f"'{comp_type}' → '{mapped}'"
                )
                comp["type"] = mapped

    result.passed = len(result.fixes) == 0
    return result


# ---------------------------------------------------------------------------
# AUTH_BOOT — strategy, password, rate-limit, expiry
# ---------------------------------------------------------------------------

def _repair_auth(config_dict: dict[str, Any]) -> BootCheckResult:
    """Validate and repair auth schema for bootability."""
    result = BootCheckResult(name="auth_boot")
    auth = config_dict.get("auth", {})

    # --- strategy must be "jwt" ---
    if auth.get("strategy") != "jwt":
        result.fixes.append(
            f"AUTH: strategy '{auth.get('strategy')}' → forced to 'jwt'"
        )
        auth["strategy"] = "jwt"

    # --- password_storage must be "bcrypt" ---
    if auth.get("password_storage") != "bcrypt":
        result.fixes.append(
            f"AUTH: password_storage '{auth.get('password_storage')}' → forced to 'bcrypt'"
        )
        auth["password_storage"] = "bcrypt"

    # --- rate_limit_enabled must be true ---
    if not auth.get("rate_limit_enabled"):
        result.fixes.append("AUTH: rate_limit_enabled was missing/false → set to true")
        auth["rate_limit_enabled"] = True

    if not auth.get("rate_limit_requests_per_minute"):
        auth["rate_limit_requests_per_minute"] = 60
        result.fixes.append("AUTH: rate_limit_requests_per_minute missing → set to 60")

    # --- token_expiry must be present ---
    if not auth.get("token_expiry"):
        auth["token_expiry"] = "24h"
        result.fixes.append("AUTH: token_expiry missing → set to '24h'")

    # --- roles must be non-empty ---
    if not auth.get("roles"):
        auth["roles"] = ["user", "admin"]
        result.fixes.append("AUTH: roles empty → added ['user', 'admin']")

    result.passed = len(result.fixes) == 0
    return result


# ---------------------------------------------------------------------------
# Cross-check: referential integrity after repairs
# ---------------------------------------------------------------------------

def _cross_check(config_dict: dict[str, Any]) -> BootCheckResult:
    """Cross-check referential integrity after all boot repairs."""
    result = BootCheckResult(name="cross_check")
    db = config_dict.get("db", {})
    api = config_dict.get("api", {})
    ui = config_dict.get("ui", {})
    domain = config_dict.get("domain", {})

    # Collect existing table names
    table_names = {t.get("name", "") for t in db.get("tables", [])}

    # 1. FK columns must reference existing tables
    for table in db.get("tables", []):
        for col in table.get("columns", []):
            fk = col.get("foreign_key")
            if fk and "." in fk:
                ref_table = fk.split(".")[0]
                if ref_table not in table_names:
                    result.fixes.append(
                        f"CROSS: FK '{fk}' in table '{table.get('name')}' "
                        f"references non-existent table '{ref_table}' — "
                        f"adding stub table"
                    )
                    # Add stub table
                    stub = {
                        "name": ref_table,
                        "entity": ref_table.rstrip("s").title(),
                        "columns": [
                            {"name": "id", "type": "UUID", "primary_key": True, "nullable": False},
                            {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                            {"name": "updated_at", "type": "TIMESTAMP", "nullable": False},
                        ],
                        "indexes": [],
                    }
                    db.get("tables", []).append(stub)
                    table_names.add(ref_table)

    # 2. API resource entities must exist in domain
    domain_entity_names = {e.get("name", "") for e in domain.get("entities", [])}
    for resource in api.get("resources", []):
        entity = resource.get("entity", "")
        if entity and entity not in domain_entity_names:
            result.fixes.append(
                f"CROSS: API resource '{resource.get('name')}' references entity "
                f"'{entity}' not in domain — adding stub entity"
            )
            domain.setdefault("entities", []).append({
                "name": entity,
                "fields": [{"name": "id", "type": "uuid", "required": True, "unique": True}],
            })
            domain_entity_names.add(entity)

    # 3. UI data_source must map to API endpoint paths
    api_paths: set[str] = set()
    for resource in api.get("resources", []):
        for ep in resource.get("endpoints", []):
            method = ep.get("method", "")
            path = ep.get("path", "")
            api_paths.add(f"{method} {path}")
            api_paths.add(path)

    for page in ui.get("pages", []):
        for comp in page.get("components", []):
            ds = comp.get("data_source")
            if ds:
                # Check both "METHOD /path" and just "/path"
                ds_path = ds.split(" ")[-1] if " " in ds else ds
                matches = ds in api_paths or ds_path in api_paths
                path_matches = any(
                    ds_path == p.split(" ")[-1] if " " in p else ds_path == p
                    for p in api_paths
                )
                if not matches and not path_matches:
                    result.fixes.append(
                        f"CROSS: UI component data_source '{ds}' on page "
                        f"'{page.get('id')}' has no matching API endpoint "
                        f"— clearing data_source"
                    )
                    comp["data_source"] = None

    result.passed = len(result.fixes) == 0
    return result


# ---------------------------------------------------------------------------
# Public API — multi-pass boot repair
# ---------------------------------------------------------------------------

def _config_hash(config: dict) -> str:
    """Compute hash for oscillation detection."""
    return hashlib.md5(json.dumps(config, sort_keys=True, default=str).encode()).hexdigest()


def run_boot_repair(
    config_dict: dict[str, Any],
    max_passes: int = 3,
) -> tuple[dict[str, Any], BootRepairReport]:
    """Run all boot checks with auto-repair and oscillation detection.

    Args:
        config_dict: The AppConfig dict to validate and repair.
        max_passes: Maximum repair passes before escalation.

    Returns:
        Tuple of (repaired_config, boot_repair_report).
    """
    report = BootRepairReport()
    current = copy.deepcopy(config_dict)
    seen_hashes: list[str] = []

    for pass_num in range(1, max_passes + 1):
        h = _config_hash(current)
        if h in seen_hashes:
            report.oscillation_detected = True
            logger.warning(f"Stage 5 oscillation detected at pass {pass_num}")
            break
        seen_hashes.append(h)

        # Run all 4 boot checks (each mutates current in-place)
        db_result = _repair_db(current)
        api_result = _repair_api(current)
        ui_result = _repair_ui(current)
        auth_result = _repair_auth(current)
        cross_result = _cross_check(current)

        # Merge results into report (accumulate fixes across passes)
        report.db_boot.fixes.extend(db_result.fixes)
        report.api_boot.fixes.extend(api_result.fixes)
        report.ui_boot.fixes.extend(ui_result.fixes)
        report.auth_boot.fixes.extend(auth_result.fixes)
        report.cross_check.fixes.extend(cross_result.fixes)

        all_passed = all([
            db_result.passed,
            api_result.passed,
            ui_result.passed,
            auth_result.passed,
            cross_result.passed,
        ])

        if all_passed:
            break

    # Final status per group
    report.db_boot.passed = _repair_db(copy.deepcopy(current)).passed
    report.api_boot.passed = _repair_api(copy.deepcopy(current)).passed
    report.ui_boot.passed = _repair_ui(copy.deepcopy(current)).passed
    report.auth_boot.passed = _repair_auth(copy.deepcopy(current)).passed
    report.cross_check.passed = _cross_check(copy.deepcopy(current)).passed

    report.total_fixes = (
        len(report.db_boot.fixes) + len(report.api_boot.fixes)
        + len(report.ui_boot.fixes) + len(report.auth_boot.fixes)
        + len(report.cross_check.fixes)
    )

    # Escalate any still-failing groups
    if not report.db_boot.passed:
        report.db_boot.oscillation_detected = True
        report.db_boot.fixes.append("[ESCALATE] DB boot still failing after max passes")
    if not report.api_boot.passed:
        report.api_boot.oscillation_detected = True
        report.api_boot.fixes.append("[ESCALATE] API boot still failing after max passes")
    if not report.ui_boot.passed:
        report.ui_boot.oscillation_detected = True
        report.ui_boot.fixes.append("[ESCALATE] UI boot still failing after max passes")
    if not report.auth_boot.passed:
        report.auth_boot.oscillation_detected = True
        report.auth_boot.fixes.append("[ESCALATE] AUTH boot still failing after max passes")

    report.oscillation_detected = any([
        report.db_boot.oscillation_detected,
        report.api_boot.oscillation_detected,
        report.ui_boot.oscillation_detected,
        report.auth_boot.oscillation_detected,
    ])

    logger.info(
        f"Stage 5 boot repair: total_fixes={report.total_fixes}, "
        f"oscillation={report.oscillation_detected}, "
        f"db={report.db_boot.passed}, api={report.api_boot.passed}, "
        f"ui={report.ui_boot.passed}, auth={report.auth_boot.passed}"
    )

    return current, report


# ---------------------------------------------------------------------------
# Legacy API — generate_execution_report (for orchestrator compatibility)
# ---------------------------------------------------------------------------

def generate_execution_report(config: ValidatedAppConfig) -> ExecutionReport:
    """Generate a full execution readiness report from a ValidatedAppConfig.

    Runs boot checks on the already-validated config to produce the
    ExecutionReport expected by the orchestrator.
    """
    config_dict = config.model_dump()

    # Run all 4 boot checks (read-only — don't mutate the validated config)
    db_result = _repair_db(copy.deepcopy(config_dict))
    api_result = _repair_api(copy.deepcopy(config_dict))
    ui_result = _repair_ui(copy.deepcopy(config_dict))
    auth_result = _repair_auth(copy.deepcopy(config_dict))

    overall = all([
        db_result.passed, api_result.passed,
        ui_result.passed, auth_result.passed,
    ])

    logger.info(
        f"Stage 5 execution report: overall={'PASS' if overall else 'FAIL'} "
        f"(db={db_result.passed}, api={api_result.passed}, "
        f"ui={ui_result.passed}, auth={auth_result.passed})"
    )

    return ExecutionReport(
        db_bootable=ExecutionCheck(
            name="db_bootability",
            passed=db_result.passed,
            details=f"Checked DB tables, {len(db_result.fixes)} fixes needed",
            errors=db_result.fixes,
        ),
        api_complete=ExecutionCheck(
            name="api_completeness",
            passed=api_result.passed,
            details=f"Checked API endpoints, {len(api_result.fixes)} fixes needed",
            errors=api_result.fixes,
        ),
        ui_renderable=ExecutionCheck(
            name="ui_renderability",
            passed=ui_result.passed,
            details=f"Checked UI components, {len(ui_result.fixes)} fixes needed",
            errors=ui_result.fixes,
        ),
        auth_sane=ExecutionCheck(
            name="auth_sanity",
            passed=auth_result.passed,
            details=f"Checked auth config, {len(auth_result.fixes)} fixes needed",
            errors=auth_result.fixes,
        ),
        overall_pass=overall,
    )
