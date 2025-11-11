"""
Tendril JWT Verifier

Responsibilities:
 - Validate JWTs issued by Tendril signers
 - Use cryptographic material from tendril.jwt.secrets (public keys or JWKS)
 - Apply configuration from tendril.config (issuer, algorithms)
 - Cross-check audience, and issuer claims
 - Return structured verification results or raise exceptions on failure
"""

import jwt
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from tendril.config import (
    AUTH_JWT_ISSUER,
    AUTH_JWT_ALGORITHMS,
)
from . import secrets
from .common import domains

from .exceptions import JWTDomainError
from .exceptions import JWTIssuerError
from .exceptions import JWTExpiredError
from .exceptions import JWTNotYetValidError
from .exceptions import JWTAudienceError
from .exceptions import JWTSignatureError
from .exceptions import JWTVerificationError

from tendril.utils.log import get_logger
logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Verification logic
# ---------------------------------------------------------------------
def _select_public_key(token_headers: Dict[str, Any]) -> str:
    """
    Select a public key for verification based on the token header.
    Uses the 'kid' header to find a match in secrets.jwks if available.
    Falls back to secrets.public_key.
    """
    kid = token_headers.get("kid")
    if hasattr(secrets, "jwks") and secrets.jwks:
        keys = secrets.jwks.get("keys", [])
        for key in keys:
            if key.get("kid") == kid:
                if key.get("use") == "revoked":
                    continue
                # Convert JWKS to PEM if necessary
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    if hasattr(secrets, "public_key") and secrets.public_key:
        return secrets.public_key
    raise JWTSignatureError(f"No suitable public key found for token verification for kid {kid}")


def _get_domain_from_claims(claims: Dict[str, Any]) -> Optional[str]:
    """
    Determine which domain this token belongs to.
    """
    if "aud" in claims:
        for domain_name, domain in domains.items():
            if domain.get_audience() == claims["aud"]:
                return domain_name
    return None


def verify_token(token: str, expected_audience: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify a JWT and return its decoded claims if valid.

    Steps:
      1. Decode token header to select key (via kid or fallback)
      2. Decode and verify JWT signature
      3. Verify issuer and audience
      4. Determine domain and attach it to the result

    Raises JWTVerificationError (or subclass) on failure.
    """
    try:
        unverified_headers = jwt.get_unverified_header(token)
    except jwt.InvalidTokenError as e:
        raise JWTSignatureError(f"Malformed token: {e}") from e

    key = _select_public_key(unverified_headers)

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=AUTH_JWT_ALGORITHMS,
            audience=expected_audience,
            issuer=AUTH_JWT_ISSUER,
            options={"require": ["exp", "iat", "nbf"], "verify_signature": True},
        )
    except jwt.ImmatureSignatureError as e:
        raise JWTNotYetValidError("Token is not yet valid") from e
    except jwt.ExpiredSignatureError as e:
        raise JWTExpiredError("Token has expired") from e
    except jwt.InvalidAudienceError as e:
        raise JWTAudienceError(f"Invalid audience: {e}") from e
    except jwt.InvalidIssuerError as e:
        raise JWTIssuerError(f"Issuer mismatch: {e}") from e
    except jwt.InvalidSignatureError as e:
        raise JWTSignatureError(f"Signature verification failed: {e}") from e
    except jwt.PyJWTError as e:
        raise JWTVerificationError(f"Token verification failed: {e}") from e

    # Determine domain
    domain_name = _get_domain_from_claims(claims)
    if not domain_name:
        raise JWTDomainError("Unable to determine JWT domain")
    if domain_name not in domains:
        raise JWTDomainError(f"Unknown domain '{domain_name}'")

    domain = domains[domain_name]

    # Attach verification metadata
    result = {
        "claims": claims,
        "domain": domain_name,
        "domain_obj": domain,
        "verified_at": datetime.now(timezone.utc),
        "headers": unverified_headers,
    }

    logger.debug(
        "Verified JWT for domain=%s, sub=%s, exp=%s",
        domain_name,
        claims.get("sub"),
        datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
    )

    return result


def verify_and_extract(token: str, claim: str, audience: Optional[str] = None) -> Any:
    """
    Convenience wrapper that verifies a token and extracts a specific claim.
    """
    verified = verify_token(token, expected_audience=audience)
    claims = verified["claims"]
    if claim not in claims:
        raise KeyError(f"Claim '{claim}' not found in token")
    return claims[claim]
