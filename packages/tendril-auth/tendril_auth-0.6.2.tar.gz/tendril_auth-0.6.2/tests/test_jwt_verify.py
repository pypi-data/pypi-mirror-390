import time
import pytest
import jwt
from datetime import datetime, timedelta, timezone

from tendril.jwt import sign, verify

# ---------------------------------------------------------------------
# Fixtures and mocks
# ---------------------------------------------------------------------
class DummyDomain:
    def __init__(self, name="dummy"):
        self.name = name
        self.jwt_spec = {"claims": {"sub": "user.email"}, "validity": 60, "ttl": 0}

    def get_audience(self):
        return f"{self.name}_audience"


class DummyUser:
    def __init__(self, email="verify_user@example.com"):
        self.email = email
        self.puid = "verify-user-uuid"


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Patch secrets and config for all tests."""
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    PRIVATE_KEY = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    PUBLIC_KEY = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    monkeypatch.setattr(sign, "secrets", type("s", (), {
        "private_key": PRIVATE_KEY,
        "public_key": PUBLIC_KEY,
        "kid": "kid-001",
    }))
    monkeypatch.setattr(verify, "secrets", sign.secrets)

    monkeypatch.setattr(sign, "AUTH_JWT_ALGORITHMS", ["RS256"])
    monkeypatch.setattr(sign, "AUTH_JWT_ISSUER", "https://tendril.test")
    monkeypatch.setattr(sign, "AUTH_JWT_TTL", 0)
    monkeypatch.setattr(sign, "AUTH_JWT_VALIDITY", 60)

    monkeypatch.setattr(verify, "AUTH_JWT_ALGORITHMS", ["RS256"])
    monkeypatch.setattr(verify, "AUTH_JWT_ISSUER", "https://tendril.test")

    dummy_domain = DummyDomain()
    monkeypatch.setattr(sign, "domains", {"dummy": dummy_domain})
    monkeypatch.setattr(verify, "domains", {"dummy": dummy_domain})
    yield


def _make_token(domain="dummy", email="verify_user@example.com"):
    user = DummyUser(email=email)
    return sign.generate_token(domain, user)


# ---------------------------------------------------------------------
# Positive cases
# ---------------------------------------------------------------------
def test_valid_token_verification():
    """A correctly signed token should verify successfully."""
    token = _make_token()
    result = verify.verify_token(token, expected_audience="dummy_audience")

    claims = result["claims"]
    assert claims["sub"] == "verify_user@example.com"
    assert claims["aud"] == "dummy_audience"
    assert claims["iss"] == "https://tendril.test"
    assert result["domain"] == "dummy"


def test_verify_and_extract_claim():
    """verify_and_extract should return a single claim."""
    token = _make_token()
    sub = verify.verify_and_extract(token, "sub", audience="dummy_audience")
    assert sub == "verify_user@example.com"


def test_domain_determined_by_audience(monkeypatch):
    """Token with only audience should still infer domain."""
    dom = DummyDomain(name="alt")
    monkeypatch.setattr(sign, "domains", {"alt": dom})
    monkeypatch.setattr(verify, "domains", {"alt": dom})

    token = sign.generate_token("alt", DummyUser())
    result = verify.verify_token(token, expected_audience="alt_audience")

    assert result["domain"] == "alt"
    assert "sub" in result["claims"]


# ---------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------
def test_invalid_signature(monkeypatch):
    """A token signed with a different key must fail."""
    token = _make_token()
    # Replace verify key with unrelated one
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    wrong_pub = wrong_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    monkeypatch.setattr(verify.secrets, "public_key", wrong_pub)

    with pytest.raises(verify.JWTSignatureError):
        verify.verify_token(token, expected_audience="dummy_audience")


def test_wrong_audience(monkeypatch):
    """Token with incorrect audience must fail."""
    token = _make_token()
    with pytest.raises(verify.JWTAudienceError):
        verify.verify_token(token, expected_audience="other_audience")


def test_wrong_issuer(monkeypatch):
    """Token with incorrect issuer must fail."""
    token = _make_token()
    monkeypatch.setattr(verify, "AUTH_JWT_ISSUER", "https://evil.issuer")
    with pytest.raises(verify.JWTIssuerError):
        verify.verify_token(token, expected_audience="dummy_audience")


def test_expired_token(monkeypatch):
    """Token past exp must raise JWTExpiredError."""
    domain = DummyDomain()
    domain.jwt_spec["claims"] = {"sub": "user.email"}
    domain.jwt_spec["validity"] = -5  # already expired
    sign.domains["expired"] = domain
    verify.domains["expired"] = domain

    token = _make_token(domain="expired")
    with pytest.raises(verify.JWTExpiredError):
        verify.verify_token(token, expected_audience="expired_audience")


def test_not_yet_valid_token(monkeypatch):
    """Token with future nbf must raise JWTExpiredError."""
    domain = DummyDomain()
    domain.jwt_spec["claims"] = {"sub": "user.email"}
    domain.jwt_spec["ttl"] = 60  # not valid yet
    sign.domains["future"] = domain
    verify.domains["future"] = domain

    token = _make_token(domain="future")
    with pytest.raises(verify.JWTNotYetValidError):
        verify.verify_token(token, expected_audience="future_audience")


def test_unknown_domain(monkeypatch):
    """Token with an unrecognized audience should raise JWTDomainError."""
    domain = DummyDomain(name="weird")
    domain.jwt_spec["claims"] = {"sub": "user.email"}
    sign.domains["weird"] = domain

    token = _make_token(domain="weird")
    # Remove domain from verify side
    monkeypatch.setattr(verify, "domains", {})

    with pytest.raises(verify.JWTDomainError):
        verify.verify_token(token, expected_audience="weird_audience")


def test_malformed_token():
    """Corrupted token must fail early."""
    bad_token = "this.is.not.a.jwt"
    with pytest.raises(verify.JWTSignatureError):
        verify.verify_token(bad_token)


def test_claim_extraction_missing_claim():
    """verify_and_extract should raise KeyError for missing claim."""
    token = _make_token()
    with pytest.raises(KeyError):
        verify.verify_and_extract(token, "nonexistent", audience="dummy_audience")


# ---------------------------------------------------------------------
# JWKS handling
# ---------------------------------------------------------------------
def test_jwks_key_selection(monkeypatch):
    """Verify JWKS-based key selection using kid header."""
    import json
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from jwt.algorithms import RSAAlgorithm

    # Generate new RSA keypair
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    # Build proper JWK dict
    jwk_json = RSAAlgorithm.to_jwk(key.public_key())
    jwk_obj = json.loads(jwk_json)
    jwk_obj["kid"] = "test-kid"

    # Patch secrets with JWKS
    monkeypatch.setattr(sign, "secrets", type("s", (), {
        "private_key": priv_pem,
        "public_key": pub_pem,
        "kid": "test-kid",
        "jwks": {"keys": [jwk_obj]},
    }))
    monkeypatch.setattr(verify, "secrets", sign.secrets)

    # Patch domain
    domain = DummyDomain(name="jwks")
    domain.jwt_spec["claims"] = {"sub": "user.email"}
    sign.domains["jwks"] = domain
    verify.domains["jwks"] = domain

    # Generate token using the JWKS-backed key
    token = sign.generate_token("jwks", DummyUser())

    # Peek into token to find its actual audience. This is for testing only
    unverified = jwt.decode(token, options={"verify_signature": False})
    actual_aud = unverified.get("aud")
    assert actual_aud == "jwks_audience"
    if isinstance(actual_aud, list) and len(actual_aud) == 1:
        actual_aud = actual_aud[0]

    # Verify token using JWKS key selection
    result = verify.verify_token(token, expected_audience=actual_aud)

    # Assertions
    assert result["domain"] == "jwks"
    assert result["claims"]["sub"] == "verify_user@example.com"
    assert result["claims"]["aud"] == actual_aud
    assert result["headers"]["kid"] == "test-kid"
