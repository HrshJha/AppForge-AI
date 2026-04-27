"""Cross-layer consistency rules.

All 10 rules are implemented as pure functions that take a
ValidatedAppConfig and return a list of ValidationViolation.
Each rule is independently testable.
"""

from __future__ import annotations

from app.schemas.common import ValidationViolation, Severity
from app.schemas.app_config import ValidatedAppConfig


# ---------------------------------------------------------------------------
# CL-001: API entities must exist in domain
# ---------------------------------------------------------------------------

def check_api_entities_in_domain(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """Every api.resources[].entity must exist in domain.entities[].name."""
    violations = []
    domain_names = {e.name for e in config.domain.entities}

    for resource in config.api.resources:
        if resource.entity not in domain_names:
            violations.append(
                ValidationViolation(
                    rule_id="CL-001",
                    layer="api",
                    message=f"API resource '{resource.name}' references entity '{resource.entity}' not found in domain entities: {domain_names}",
                    severity=Severity.ERROR,
                    fix_hint=f"Add entity '{resource.entity}' to domain.entities or fix the API resource entity reference",
                    field_path=f"api.resources.{resource.name}.entity",
                )
            )
    return violations


# ---------------------------------------------------------------------------
# CL-002: UI data sources must map to API endpoints
# ---------------------------------------------------------------------------

def check_ui_data_sources_in_api(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """Every ui.pages[].components[].data_source must resolve to a defined API endpoint."""
    violations = []

    # Build set of all defined API endpoint paths (METHOD /path)
    api_endpoints = set()
    for resource in config.api.resources:
        for endpoint in resource.endpoints:
            api_endpoints.add(f"{endpoint.method.value} {endpoint.path}")
            # Also add just the path for flexible matching
            api_endpoints.add(endpoint.path)

    for page in config.ui.pages:
        for i, component in enumerate(page.components):
            if component.data_source:
                # data_source might be "GET /api/contacts" or just "/api/contacts"
                if (
                    component.data_source not in api_endpoints
                    and component.data_source.split(" ")[-1] not in {ep.split(" ")[-1] for ep in api_endpoints}
                ):
                    violations.append(
                        ValidationViolation(
                            rule_id="CL-002",
                            layer="ui",
                            message=f"Page '{page.id}' component [{i}] data_source '{component.data_source}' not found in API endpoints",
                            severity=Severity.ERROR,
                            fix_hint=f"Add an API endpoint matching '{component.data_source}' or fix the data_source reference",
                            field_path=f"ui.pages.{page.id}.components[{i}].data_source",
                        )
                    )
    return violations


# ---------------------------------------------------------------------------
# CL-003: Logic rule roles must exist in auth
# ---------------------------------------------------------------------------

def check_logic_roles_in_auth(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """All roles referenced in logic.rules[].condition must exist in auth.roles."""
    violations = []
    auth_roles = set(config.auth.roles)

    for rule in config.logic.rules:
        # Extract role references from condition string
        # Conditions look like "user.role == admin" or "role in [admin, premium_user]"
        for role in auth_roles:
            pass  # roles that exist are fine

        # Check if condition references any role-like strings
        condition = rule.condition.lower()
        for word in condition.replace("==", " ").replace("!=", " ").replace(",", " ").split():
            word = word.strip("[]()\"' ")
            if word and word not in ("user", "role", "in", "not", "and", "or", "true", "false"):
                if word not in {r.lower() for r in auth_roles}:
                    # Could be a role reference that doesn't exist
                    if any(keyword in condition for keyword in ["role", "permission"]):
                        violations.append(
                            ValidationViolation(
                                rule_id="CL-003",
                                layer="logic",
                                message=f"Logic rule '{rule.id}' condition references possible role '{word}' not found in auth.roles: {auth_roles}",
                                severity=Severity.WARNING,
                                fix_hint=f"Add role '{word}' to auth.roles or update the logic rule condition",
                                field_path=f"logic.rules.{rule.id}.condition",
                            )
                        )
    return violations


# ---------------------------------------------------------------------------
# CL-004: DB fields must match domain entity fields
# ---------------------------------------------------------------------------

def check_db_fields_match_domain(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """DB table columns (excluding meta fields) should be backed by domain entity fields."""
    violations = []
    META_FIELDS = {"id", "created_at", "updated_at", "deleted_at"}

    # Build domain entity field map
    domain_fields: dict[str, set[str]] = {}
    for entity in config.domain.entities:
        fields = set()
        for f in entity.fields:
            if isinstance(f, dict):
                fields.add(f.get("name", ""))
            elif isinstance(f, str):
                fields.add(f)
        domain_fields[entity.name] = fields

    for table in config.db.tables:
        if table.entity not in domain_fields:
            violations.append(
                ValidationViolation(
                    rule_id="CL-004",
                    layer="db",
                    message=f"DB table '{table.name}' references entity '{table.entity}' not found in domain",
                    severity=Severity.ERROR,
                    fix_hint=f"Add entity '{table.entity}' to domain.entities",
                    field_path=f"db.tables.{table.name}.entity",
                )
            )
            continue

        entity_fields = domain_fields[table.entity]
        for col in table.columns:
            if col.name not in META_FIELDS and col.name not in entity_fields:
                # Check if it's a foreign key field (e.g., user_id)
                if col.foreign_key:
                    continue  # FK fields are auto-generated, not in domain
                violations.append(
                    ValidationViolation(
                        rule_id="CL-004",
                        layer="db",
                        message=f"DB table '{table.name}' column '{col.name}' not backed by domain entity '{table.entity}' fields: {entity_fields}",
                        severity=Severity.WARNING,
                        fix_hint=f"Add field '{col.name}' to domain entity '{table.entity}' or remove from DB schema",
                        field_path=f"db.tables.{table.name}.columns.{col.name}",
                    )
                )
    return violations


# ---------------------------------------------------------------------------
# CL-005: Premium features require payment flow
# ---------------------------------------------------------------------------

def check_premium_requires_payment(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """If premium features exist, a payment-related API resource must exist."""
    violations = []

    # Check if any page or guard references premium
    has_premium = False
    for page in config.ui.pages:
        if "premium" in " ".join(page.roles).lower():
            has_premium = True
            break
    for guard in config.auth.guards:
        if "premium" in " ".join(guard.required_roles).lower():
            has_premium = True
            break
    for perm in config.auth.permissions:
        if "premium" in perm.role.lower():
            has_premium = True
            break

    if has_premium:
        payment_resources = [
            r for r in config.api.resources
            if any(kw in r.name.lower() for kw in ["payment", "subscription", "billing", "plan", "stripe"])
        ]
        if not payment_resources:
            violations.append(
                ValidationViolation(
                    rule_id="CL-005",
                    layer="api",
                    message="Premium features detected but no payment/subscription API resource found",
                    severity=Severity.ERROR,
                    fix_hint="Add a payment or subscription API resource with billing endpoints",
                    field_path="api.resources",
                )
            )
    return violations


# ---------------------------------------------------------------------------
# CL-006: Admin role requires admin endpoint
# ---------------------------------------------------------------------------

def check_admin_requires_endpoint(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """If 'admin' role exists, at least one admin-only endpoint must exist."""
    violations = []

    if "admin" in config.auth.roles:
        admin_endpoints = []
        for resource in config.api.resources:
            for endpoint in resource.endpoints:
                if "admin" in [r.lower() for r in endpoint.roles]:
                    admin_endpoints.append(endpoint)

        admin_pages = [p for p in config.ui.pages if "admin" in [r.lower() for r in p.roles]]

        if not admin_endpoints and not admin_pages:
            violations.append(
                ValidationViolation(
                    rule_id="CL-006",
                    layer="api",
                    message="Admin role defined but no admin-only endpoints or pages found",
                    severity=Severity.WARNING,
                    fix_hint="Add at least one endpoint or page restricted to the admin role",
                    field_path="api.resources",
                )
            )
    return violations


# ---------------------------------------------------------------------------
# CL-007: Payment entities require Stripe webhook
# ---------------------------------------------------------------------------

def check_payment_requires_webhook(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """If payment-related entities/resources exist, a webhook endpoint is required."""
    violations = []

    payment_resources = [
        r for r in config.api.resources
        if any(kw in r.name.lower() for kw in ["payment", "subscription", "billing", "stripe"])
    ]

    if payment_resources:
        webhook_endpoints = [
            ep
            for r in config.api.resources
            for ep in r.endpoints
            if "webhook" in ep.path.lower()
        ]
        if not webhook_endpoints:
            violations.append(
                ValidationViolation(
                    rule_id="CL-007",
                    layer="api",
                    message="Payment resources exist but no webhook endpoint found",
                    severity=Severity.WARNING,
                    fix_hint="Add a POST /api/webhooks/stripe endpoint for payment webhook handling",
                    field_path="api.resources",
                )
            )
    return violations


# ---------------------------------------------------------------------------
# CL-008: Auth must enforce JWT expiry
# ---------------------------------------------------------------------------

def check_auth_jwt_expiry(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """Auth token_expiry must be set and reasonable (≤ 24h)."""
    violations = []

    if not config.auth.token_expiry:
        violations.append(
            ValidationViolation(
                rule_id="CL-008",
                layer="auth",
                message="Auth token_expiry is not set — JWT tokens must have an expiry",
                severity=Severity.ERROR,
                fix_hint="Set auth.token_expiry to a value like '24h'",
                field_path="auth.token_expiry",
            )
        )
    else:
        # Parse duration string and check if it's ≤ 24h
        expiry = config.auth.token_expiry
        hours = _parse_duration_hours(expiry)
        if hours is not None and hours > 24:
            violations.append(
                ValidationViolation(
                    rule_id="CL-008",
                    layer="auth",
                    message=f"Auth token_expiry '{expiry}' exceeds 24 hours — security risk",
                    severity=Severity.WARNING,
                    fix_hint="Set auth.token_expiry to 24h or less",
                    field_path="auth.token_expiry",
                )
            )

    return violations


def _parse_duration_hours(duration: str) -> float | None:
    """Parse a duration string like '24h', '7d', '30m' to hours."""
    import re
    match = re.match(r"^(\d+)\s*(h|d|m|hr|hrs|hours|days|min|mins)$", duration.strip().lower())
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2)
    if unit in ("h", "hr", "hrs", "hours"):
        return float(value)
    elif unit in ("d", "days"):
        return float(value * 24)
    elif unit in ("m", "min", "mins"):
        return float(value / 60)
    return None


# ---------------------------------------------------------------------------
# CL-009: No nullable FK without annotation
# ---------------------------------------------------------------------------

def check_nullable_fk(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """DB foreign key columns should not be nullable without explicit reason."""
    violations = []

    for table in config.db.tables:
        for col in table.columns:
            if col.foreign_key and col.nullable:
                violations.append(
                    ValidationViolation(
                        rule_id="CL-009",
                        layer="db",
                        message=f"DB table '{table.name}' column '{col.name}' is a nullable FK — consider making it non-nullable",
                        severity=Severity.WARNING,
                        fix_hint=f"Set nullable=false for FK column '{col.name}' or document why it's nullable",
                        field_path=f"db.tables.{table.name}.columns.{col.name}",
                    )
                )
    return violations


# ---------------------------------------------------------------------------
# CL-010: All API endpoints have auth_required
# ---------------------------------------------------------------------------

def check_endpoints_have_auth(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """Every API endpoint must have an explicit auth_required flag (defaults to true)."""
    violations = []

    for resource in config.api.resources:
        for endpoint in resource.endpoints:
            # auth_required defaults to True in our model, so this rule
            # primarily catches cases where it's explicitly set to False
            # for non-public endpoints
            if not endpoint.auth_required:
                # Only flag if it's not a public endpoint (webhooks, health)
                public_paths = ["/health", "/webhook", "/public"]
                if not any(pub in endpoint.path.lower() for pub in public_paths):
                    violations.append(
                        ValidationViolation(
                            rule_id="CL-010",
                            layer="api",
                            message=f"Endpoint {endpoint.method.value} {endpoint.path} has auth_required=false — verify this is intentional",
                            severity=Severity.WARNING,
                            fix_hint="Set auth_required=true unless this is a public endpoint",
                            field_path=f"api.resources.{resource.name}.endpoints.{endpoint.path}",
                        )
                    )
    return violations


# ---------------------------------------------------------------------------
# Registry of all rules
# ---------------------------------------------------------------------------

ALL_RULES = [
    ("CL-001", "API entities must exist in domain", check_api_entities_in_domain),
    ("CL-002", "UI data sources must map to API endpoints", check_ui_data_sources_in_api),
    ("CL-003", "Logic rule roles must exist in auth", check_logic_roles_in_auth),
    ("CL-004", "DB fields must match domain entity fields", check_db_fields_match_domain),
    ("CL-005", "Premium features require payment flow", check_premium_requires_payment),
    ("CL-006", "Admin role requires admin endpoint", check_admin_requires_endpoint),
    ("CL-007", "Payment entities require Stripe webhook", check_payment_requires_webhook),
    ("CL-008", "Auth must enforce JWT expiry", check_auth_jwt_expiry),
    ("CL-009", "No nullable FK without annotation", check_nullable_fk),
    ("CL-010", "All API endpoints have auth_required", check_endpoints_have_auth),
]


def run_all_cross_layer_rules(config: ValidatedAppConfig) -> list[ValidationViolation]:
    """Run all cross-layer consistency rules and return violations."""
    violations = []
    for rule_id, description, check_fn in ALL_RULES:
        try:
            rule_violations = check_fn(config)
            violations.extend(rule_violations)
        except Exception as e:
            violations.append(
                ValidationViolation(
                    rule_id=rule_id,
                    layer="cross_layer",
                    message=f"Rule '{description}' crashed: {str(e)}",
                    severity=Severity.ERROR,
                    fix_hint="Internal error — check the validation rule implementation",
                )
            )
    return violations
