"""Internal authentication for Gateway internal callers."""

from __future__ import annotations

import hmac
import secrets
from types import SimpleNamespace

from deerflow.runtime.user_context import DEFAULT_USER_ID

INTERNAL_AUTH_HEADER_NAME = "X-DeerFlow-Internal-Token"
_INTERNAL_AUTH_CONTEXT = "deerflow-internal-auth-v1"


def _get_internal_auth_token() -> str:
    from app.gateway.auth.config import get_auth_config

    return hmac.digest(get_auth_config().jwt_secret.encode(), _INTERNAL_AUTH_CONTEXT.encode(), "sha256").hex()


def create_internal_auth_headers() -> dict[str, str]:
    """Return headers that authenticate same-process Gateway internal calls."""
    return {INTERNAL_AUTH_HEADER_NAME: _get_internal_auth_token()}


def is_valid_internal_auth_token(token: str | None) -> bool:
    """Return True when *token* matches the process-local internal token."""
    return bool(token) and secrets.compare_digest(token, _get_internal_auth_token())


def get_internal_user():
    """Return the synthetic user used for trusted internal channel calls."""
    return SimpleNamespace(id=DEFAULT_USER_ID, system_role="internal")
