"""
Tendril JWT Signer and Verifier
--------------------------------
Produces and validates signed JWTs using RS256 by default.

Responsibilities:
 - Uses cryptographic material from tendril.jwt.secrets
 - Applies configuration from tendril.config (issuer, algorithm, validity, ttl)
 - Retrieves per-domain claim specifications from tendril.jwt.common.domains
 - Generates and verifies JWTs in accordance with each domain's jwt_spec

Domain jwt_spec format:
    {
        "claims": {
            "sub": "user.email",             # user.email → claim value
            "org": "user.get_org_id",        # user.get_org_id(context)
            "ip":  "context.ip",             # context.ip
        },
        "validity": 3600,
        "ttl": 0,
    }

Claim resolution rules:
 - Each claim spec is a string of the form "<ctx>.<key>".
 - <ctx> must exist in the `context` dict or be the literal string 'context'.
 - <key> is an attribute or callable of that object.
 - Callables may be synchronous or asynchronous; both are supported.
 - Any missing objects, attributes, or failed call results raise immediately.
"""

import jwt
import uuid
import asyncio
from datetime import timezone, datetime, timedelta
from typing import Any, Optional, List, Dict

from tendril.config import (
    AUTH_JWT_ISSUER,
    AUTH_JWT_TTL,
    AUTH_JWT_VALIDITY,
    AUTH_JWT_ALGORITHMS,
)
from . import secrets
from .common import domains

from tendril.utils.asyncif import run_callable_blocking, run_callable_async
from tendril.utils.log import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------
# Claim resolution
# ---------------------------------------------------------------------
def _get_context_and_attr(claim_spec: str, context: Dict[str, Any]):
    """Split '<ctx>.<key>' and retrieve ctx_obj."""
    if not isinstance(claim_spec, str):
        raise ValueError(f"Unsupported claim_spec type: {type(claim_spec).__name__}")
    try:
        ctx_name, attr = claim_spec.split(".", 1)
    except ValueError:
        raise ValueError(f"Invalid claim_spec format '{claim_spec}', expected '<ctx>.<key>'")

    ctx_obj = context if ctx_name == "context" else context.get(ctx_name)
    if ctx_obj is None:
        raise AttributeError(f"Missing context object '{ctx_name}' for claim '{claim_spec}'")
    return ctx_obj, attr


def _resolve_claim_sync(claim_spec: str, context: Dict[str, Any]) -> Any:
    """Resolve a single claim synchronously using run_callable_blocking."""
    ctx_obj, attr = _get_context_and_attr(claim_spec, context)
    value = getattr(ctx_obj, attr, None)
    if value is None:
        raise ValueError(f"Missing attribute '{attr}' in '{claim_spec}'")
    return run_callable_blocking(value, context) if callable(value) else value


async def _resolve_claim_async(claim_spec: str, context: Dict[str, Any]) -> Any:
    """Resolve a single claim asynchronously using run_callable_async."""
    ctx_obj, attr = _get_context_and_attr(claim_spec, context)
    value = getattr(ctx_obj, attr, None)
    if value is None:
        raise ValueError(f"Missing attribute '{attr}' in '{claim_spec}'")
    if callable(value):
        return await run_callable_async(value, context)
    if asyncio.iscoroutine(value):
        return await value
    return value


# ---------------------------------------------------------------------
# Core payload builder
# ---------------------------------------------------------------------
def _build_base_payload(domain, now: datetime) -> Dict[str, Any]:
    """Construct base JWT payload shared by all modes."""
    validity = domain.jwt_spec.get("validity", AUTH_JWT_VALIDITY)
    ttl = domain.jwt_spec.get("ttl", AUTH_JWT_TTL)
    aud = domain.get_audience()

    payload = {
        "iss": AUTH_JWT_ISSUER,
        "exp": now + timedelta(seconds=validity + ttl),
        "nbf": now + timedelta(seconds=ttl),
        "iat": now,
        "jti": uuid.uuid4().hex,
    }

    if aud:
        payload["aud"] = aud

    return payload


def _sign_payload(payload: dict) -> str:
    """Sign and return JWT string."""
    if not secrets.private_key:
        raise RuntimeError("Private key not loaded; cannot sign JWTs")
    headers = {"kid": secrets.kid} if secrets.kid else {}
    try:
        token = jwt.encode(payload, secrets.private_key,
                           algorithm=AUTH_JWT_ALGORITHMS[0], headers=headers)
    except Exception as e:
        raise RuntimeError(f"JWT signing failed: {e}")
    return token.decode() if isinstance(token, bytes) else token


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def generate_token(domain_name: str, user: Any, scopes_req: Optional[List[str]] = None) -> str:
    """
    Generate a signed JWT synchronously for the given domain.
    """
    if domain_name not in domains:
        raise ValueError(f"Unknown JWT domain: {domain_name}")

    domain = domains[domain_name]
    now = datetime.now(timezone.utc)
    payload = _build_base_payload(domain, now)
    context = {"user": user, "domain": domain, "scopes_req": scopes_req or []}

    claims = domain.jwt_spec.get("claims", {})
    if not isinstance(claims, dict):
        raise ValueError(f"Domain {domain_name!r}: jwt_spec['claims'] must be a dict")

    for name, spec in claims.items():
        payload[name] = _resolve_claim_sync(spec, context)

    token = _sign_payload(payload)

    logger.debug("Generated JWT for domain=%s user=%s exp=%s",
                 domain_name, getattr(user, "puid", None), payload["exp"])
    return token


async def generate_token_async(domain_name: str, user: Any, scopes_req: Optional[List[str]] = None) -> str:
    """
    Generate a signed JWT asynchronously for the given domain.
    """
    if domain_name not in domains:
        raise ValueError(f"Unknown JWT domain: {domain_name}")

    domain = domains[domain_name]
    now = datetime.now(timezone.utc)
    payload = _build_base_payload(domain, now)
    context = {"user": user, "domain": domain, "scopes_req": scopes_req or []}

    claims = domain.jwt_spec.get("claims", {})
    if not isinstance(claims, dict):
        raise ValueError(f"Domain {domain_name!r}: jwt_spec['claims'] must be a dict")

    # Concurrently resolve async claims
    resolved = await asyncio.gather(
        *[_resolve_claim_async(spec, context) for spec in claims.values()],
        return_exceptions=False,
    )

    for (name, value) in zip(claims.keys(), resolved):
        payload[name] = value

    token = _sign_payload(payload)

    logger.debug("Generated async JWT for domain=%s user=%s exp=%s",
                 domain_name, getattr(user, "puid", None), payload["exp"])
    return token
