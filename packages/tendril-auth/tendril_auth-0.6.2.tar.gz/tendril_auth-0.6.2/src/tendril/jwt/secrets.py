
"""
Tendril JWT Secrets Loader

This module handles ONLY the cryptographic key material required to
sign and verify JWTs.  It does not handle configuration such as
issuer, algorithm, or TTL — those are handled by the signers.

Expected tendril.config variables:
 - AUTH_JWKS_PATH
 - AUTH_JWT_PUBLIC_KEY
 - AUTH_JWT_PRIVATE_KEY

After load_keys() runs, the following module variables are available:
 - jwks         : Parsed JWKS (dict) if available
 - kid          : Active key ID (from JWKS)
 - public_key   : PEM-encoded public key bytes
 - private_key  : PEM-encoded private key bytes
"""

import json
from tendril.config import AUTH_JWKS_PATH
from tendril.config import AUTH_JWT_PUBLIC_KEY
from tendril.config import AUTH_JWT_PRIVATE_KEY
from tendril.utils import log
logger = log.get_logger(__name__)


public_key = None
private_key = None
jwks = None
kid = None


def _load_keys():
    global jwks
    global kid
    global private_key
    global public_key

    try:
        if AUTH_JWKS_PATH:
            with open(AUTH_JWKS_PATH, "rb") as f:
                jwks = json.load(f)
                kid = (
                        jwks.get("kid")
                        or (jwks.get("keys", [{}])[0].get("kid") if jwks.get("keys") else None)
                )
                logger.debug("Loaded JWKS from %s (kid=%s)", AUTH_JWKS_PATH, kid)
        else:
            logger.debug("No JWKS path configured.")
    except Exception as e:
        logger.warning("Could not load JWKS from %s: %s", AUTH_JWKS_PATH, e)
        jwks = None
        kid = None

    try:
        if AUTH_JWT_PUBLIC_KEY:
            with open(AUTH_JWT_PUBLIC_KEY, "rb") as f:
                public_key = f.read()
                logger.debug("Loaded public key from %s", AUTH_JWT_PUBLIC_KEY)
        else:
            logger.debug("No public key path configured.")
    except Exception as e:
        logger.error("Failed to read public key from %s: %s", AUTH_JWT_PUBLIC_KEY, e)
        public_key = None

    try:
        if AUTH_JWT_PRIVATE_KEY:
            with open(AUTH_JWT_PRIVATE_KEY, "rb") as f:
                private_key = f.read()
                logger.debug("Loaded private key from %s", AUTH_JWT_PRIVATE_KEY)
        else:
            logger.debug("No private key path configured.")
    except Exception as e:
        logger.error("Failed to read private key from %s: %s", AUTH_JWT_PRIVATE_KEY, e)
        private_key = None

try:
    _load_keys()
except Exception as e:
    logger.warning("JWT secrets not loaded on import: %s", e)
