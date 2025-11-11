import asyncio
import jwt
import pytest
from datetime import datetime, timezone

from tendril.jwt import sign

# ---------------------------------------------------------------------
# Fixtures and mocks
# ---------------------------------------------------------------------
class DummyDomain:
    def __init__(self):
        self.jwt_spec = {"claims": {}, "validity": 60, "ttl": 0}

    def get_audience(self):
        return "dummy_audience"


class DummyUser:
    def __init__(self, email="user@example.com", org_id="org-123"):
        self.email = email
        self._org_id = org_id
        self.puid = "user-uuid-001"

    # Sync callable
    def get_org_id(self, context):
        return self._org_id

    # Async callable
    async def get_org_id_async(self, context):
        await asyncio.sleep(0.01)
        return self._org_id + "-async"


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Patch secrets and config for all tests."""
    monkeypatch.setattr(sign, "secrets", type("s", (), {
        "private_key": "dummy_private_key",
        "kid": "kid123"
    }))
    monkeypatch.setattr(sign, "domains", {"dummy": DummyDomain()})
    monkeypatch.setattr(sign, "AUTH_JWT_ISSUER", "test_issuer")
    monkeypatch.setattr(sign, "AUTH_JWT_TTL", 10)
    monkeypatch.setattr(sign, "AUTH_JWT_VALIDITY", 30)
    monkeypatch.setattr(sign, "AUTH_JWT_ALGORITHMS", ["HS256"])  # symmetric for tests
    yield


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def decode_token(token):
    """Decode using the test scaffold."""
    return jwt.decode(token, key="dummy_private_key", algorithms=["HS256"], audience="dummy_audience")

# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_sync_token_basic(monkeypatch):
    """Generate a simple token with static claim."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"sub": "user.email"}
    sign.domains["dummy"] = d

    user = DummyUser()
    token = sign.generate_token("dummy", user)
    payload = decode_token(token)

    assert payload["iss"] == "test_issuer"
    assert payload["aud"] == "dummy_audience"
    assert payload["sub"] == user.email
    assert "exp" in payload and "iat" in payload
    assert isinstance(datetime.fromtimestamp(payload["exp"], tz=timezone.utc), datetime)


def test_sync_token_with_callable(monkeypatch):
    """Sync callable claims should resolve properly."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"org": "user.get_org_id"}
    sign.domains["dummy"] = d

    user = DummyUser()
    token = sign.generate_token("dummy", user)
    payload = decode_token(token)

    assert payload["org"] == user._org_id


@pytest.mark.asyncio
async def test_async_token_with_async_callable(monkeypatch):
    """Async callable claims should be awaited properly."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"org": "user.get_org_id_async"}
    sign.domains["dummy"] = d

    user = DummyUser()
    token = await sign.generate_token_async("dummy", user)
    payload = decode_token(token)

    assert payload["org"] == user._org_id + "-async"


@pytest.mark.asyncio
async def test_async_and_sync_claims_combined(monkeypatch):
    """Multiple claims (sync + async) should all be resolved correctly."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {
        "sub": "user.email",
        "org": "user.get_org_id_async"
    }
    sign.domains["dummy"] = d

    user = DummyUser()
    token = await sign.generate_token_async("dummy", user)
    payload = decode_token(token)

    assert payload["sub"] == user.email
    assert payload["org"] == user._org_id + "-async"
    assert payload["iss"] == "test_issuer"


def test_error_on_missing_context(monkeypatch):
    """Missing context should raise cleanly."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"bad": "nocontext.attr"}
    sign.domains["dummy"] = d
    user = DummyUser()

    with pytest.raises(AttributeError):
        sign.generate_token("dummy", user)


def test_error_on_missing_attr(monkeypatch):
    """Missing attribute should raise cleanly."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"missing": "user.nonexistent"}
    sign.domains["dummy"] = d
    user = DummyUser()

    with pytest.raises(ValueError):
        sign.generate_token("dummy", user)


def test_error_on_bad_claim_format(monkeypatch):
    """Bad claim format (no dot) should raise ValueError."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"bad": "justbad"}
    sign.domains["dummy"] = d
    user = DummyUser()

    with pytest.raises(ValueError):
        sign.generate_token("dummy", user)


def test_error_on_unknown_domain(monkeypatch):
    """Unknown domain should raise ValueError."""
    user = DummyUser()
    with pytest.raises(ValueError):
        sign.generate_token("nonexistent", user)


@pytest.mark.asyncio
async def test_async_error_on_bad_claim(monkeypatch):
    """Async path should raise on invalid claim spec."""
    d = DummyDomain()
    d.jwt_spec["claims"] = {"oops": "context.nonexistent"}
    sign.domains["dummy"] = d
    user = DummyUser()

    with pytest.raises(ValueError):
        await sign.generate_token_async("dummy", user)

def test_real_rsa_sign_and_verify(monkeypatch):
    """
    End-to-end test using a real RSA keypair to ensure signing with
    private_key and verifying with public_key works.
    """
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    # Generate a temporary 2048-bit RSA keypair
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Patch the signer to use this real keypair
    monkeypatch.setattr(sign, "secrets", type("s", (), {
        "private_key": private_pem,
        "public_key": public_pem,
        "kid": "test_kid",
    }))
    monkeypatch.setattr(sign, "AUTH_JWT_ALGORITHMS", ["RS256"])
    monkeypatch.setattr(sign, "AUTH_JWT_ISSUER", "https://tendril.example")
    monkeypatch.setattr(sign, "AUTH_JWT_VALIDITY", 300)
    monkeypatch.setattr(sign, "AUTH_JWT_TTL", 0)

    # Create a simple domain and user
    domain = DummyDomain()
    domain.jwt_spec["claims"] = {"sub": "user.email"}
    sign.domains["rsa"] = domain

    user = DummyUser(email="rsa_user@example.com")

    # Generate token using real RSA key
    token = sign.generate_token("rsa", user)
    assert token, "Token should not be empty"

    # Decode and verify using the public key
    decoded = jwt.decode(
        token,
        public_pem,
        algorithms=["RS256"],
        audience=domain.get_audience(),
        options={"verify_aud": True},
    )

    # Validate claims and structure
    assert decoded["iss"] == "https://tendril.example"
    assert decoded["aud"] == "dummy_audience"
    assert decoded["sub"] == "rsa_user@example.com"
    assert "exp" in decoded and "iat" in decoded and "nbf" in decoded
