

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------
class JWTVerificationError(Exception):
    """Base class for all JWT verification errors."""


class JWTSignatureError(JWTVerificationError):
    """Raised when signature verification fails."""


class JWTExpiredError(JWTVerificationError):
    """Raised when token is expired."""


class JWTNotYetValidError(JWTVerificationError):
    """Raised when token is not yet valid."""


class JWTDomainError(JWTVerificationError):
    """Raised when the domain in the token is not recognized."""


class JWTIssuerError(JWTVerificationError):
    """Raised when the issuer does not match."""


class JWTAudienceError(JWTVerificationError):
    """Raised when the audience is invalid or missing."""
