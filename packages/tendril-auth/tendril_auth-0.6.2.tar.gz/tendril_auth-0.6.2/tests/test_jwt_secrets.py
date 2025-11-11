import json
import os
import tempfile
import pytest
from pathlib import Path

import tendril.jwt.secrets as secrets


@pytest.fixture
def temp_keys(tmp_path):
    """Generate temporary RSA PEM files and a JWKS file."""
    priv_key = tmp_path / "privateKey.pem"
    pub_key = tmp_path / "publicKey.pem"
    jwks_file = tmp_path / "jwks.json"

    # Generate RSA keypair using OpenSSL
    os.system(f"openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out {priv_key}")
    os.system(f"openssl rsa -in {priv_key} -pubout -out {pub_key}")

    # Minimal JWKS structure
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-kid",
                "use": "sig",
                "alg": "RS256",
                "n": "fake_n",
                "e": "AQAB",
            }
        ]
    }
    jwks_file.write_text(json.dumps(jwks))

    return {
        "private": priv_key,
        "public": pub_key,
        "jwks": jwks_file,
    }


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset secrets module globals before each test."""
    secrets.jwks = None
    secrets.kid = None
    secrets.private_key = None
    secrets.public_key = None
    yield
    secrets.jwks = None
    secrets.kid = None
    secrets.private_key = None
    secrets.public_key = None


def test_loads_all_keys(monkeypatch, temp_keys):
    """Verify secrets._load_keys correctly loads JWKS, private, and public keys."""
    monkeypatch.setattr(secrets, "AUTH_JWKS_PATH", str(temp_keys["jwks"]))
    monkeypatch.setattr(secrets, "AUTH_JWT_PRIVATE_KEY", str(temp_keys["private"]))
    monkeypatch.setattr(secrets, "AUTH_JWT_PUBLIC_KEY", str(temp_keys["public"]))

    secrets._load_keys()

    assert secrets.jwks is not None
    assert isinstance(secrets.jwks, dict)
    assert secrets.kid == "test-kid"
    assert secrets.private_key is not None and b"BEGIN PRIVATE KEY" in secrets.private_key
    assert secrets.public_key is not None and b"BEGIN PUBLIC KEY" in secrets.public_key


def test_handles_missing_files(monkeypatch):
    """Should not crash if files are missing; values remain None."""
    monkeypatch.setattr(secrets, "AUTH_JWKS_PATH", "/nonexistent/jwks.json")
    monkeypatch.setattr(secrets, "AUTH_JWT_PRIVATE_KEY", "/nonexistent/privateKey.pem")
    monkeypatch.setattr(secrets, "AUTH_JWT_PUBLIC_KEY", "/nonexistent/publicKey.pem")

    secrets._load_keys()

    assert secrets.jwks is None
    assert secrets.kid is None
    assert secrets.private_key is None
    assert secrets.public_key is None


def test_loads_jwks_with_nested_key(monkeypatch, tmp_path):
    """JWKS with nested 'keys' array should extract kid from first entry."""
    jwks_path = tmp_path / "jwks.json"
    jwks = {"keys": [{"kid": "nested-kid"}]}
    jwks_path.write_text(json.dumps(jwks))

    monkeypatch.setattr(secrets, "AUTH_JWKS_PATH", str(jwks_path))
    monkeypatch.setattr(secrets, "AUTH_JWT_PRIVATE_KEY", "")
    monkeypatch.setattr(secrets, "AUTH_JWT_PUBLIC_KEY", "")

    secrets._load_keys()

    assert secrets.jwks is not None
    assert secrets.kid == "nested-kid"


def test_jwks_invalid_json(monkeypatch, tmp_path):
    """Malformed JWKS should not crash, should reset jwks to None."""
    jwks_path = tmp_path / "jwks.json"
    jwks_path.write_text("{ invalid json }")

    monkeypatch.setattr(secrets, "AUTH_JWKS_PATH", str(jwks_path))
    monkeypatch.setattr(secrets, "AUTH_JWT_PRIVATE_KEY", "")
    monkeypatch.setattr(secrets, "AUTH_JWT_PUBLIC_KEY", "")

    secrets._load_keys()
    assert secrets.jwks is None
    assert secrets.kid is None


def test_partial_load(monkeypatch, temp_keys):
    """If only public key exists, it should still load successfully."""
    monkeypatch.setattr(secrets, "AUTH_JWKS_PATH", "")
    monkeypatch.setattr(secrets, "AUTH_JWT_PRIVATE_KEY", "")
    monkeypatch.setattr(secrets, "AUTH_JWT_PUBLIC_KEY", str(temp_keys["public"]))

    secrets._load_keys()
    assert secrets.public_key is not None
    assert b"PUBLIC KEY" in secrets.public_key
    assert secrets.private_key is None
    assert secrets.jwks is None
