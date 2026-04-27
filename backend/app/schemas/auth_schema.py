"""Auth schema layer – defines authentication and authorization config."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RolePermission(BaseModel):
    """Permissions assigned to a role."""
    role: str
    permissions: list[str] = Field(
        description="Permission strings, e.g. 'contacts.read', 'contacts.write', '*'"
    )


class AuthGuard(BaseModel):
    """A named auth guard for protecting routes."""
    name: str
    required_roles: list[str]
    redirect: str = "/login"


class AuthSchema(BaseModel):
    """Complete auth configuration for the generated application."""

    strategy: Literal["jwt"] = "jwt"
    token_expiry: str = Field(
        default="24h",
        description="Token expiry duration, e.g. '24h', '7d'",
    )
    refresh_token: bool = True
    password_storage: Literal["bcrypt"] = "bcrypt"
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    roles: list[str] = Field(default_factory=lambda: ["user", "admin"])
    permissions: list[RolePermission] = Field(default_factory=list)
    guards: list[AuthGuard] = Field(default_factory=list)
