#!/usr/bin/env python3
"""
generate_jwks.py — Tendril JWT JWKS Generator with Rotation & Revocation

Generates or updates a JWKS file. Supports:
  - Appending new keys
  - Limiting total key count (--max-keys)
  - Revoking specific keys (--revoke-kid)

Usage:
  python3 generate_jwks.py --public-key publicKey.pem --kid <kid> --output jwks.json [--max-keys 3]
  python3 generate_jwks.py --revoke-kid <kid> --output jwks.json
"""

import json
import base64
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def b64u(data: bytes) -> str:
    """Base64 URL-safe encoding without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def generate_jwk(public_key_pem: str, kid: str) -> dict:
    """Generate a single JWK dict for an RSA public key."""
    with open(public_key_pem, 'rb') as f:
        pubkey = serialization.load_pem_public_key(f.read(), backend=default_backend())
        if not isinstance(pubkey, rsa.RSAPublicKey):
            raise TypeError("Only RSA public keys are supported")

    numbers = pubkey.public_numbers()
    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": b64u(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")),
        "e": b64u(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")),
    }


def load_existing_jwks(path: Path) -> List[dict]:
    """Load existing JWKS keys, or an empty list if not found."""
    if not path.exists():
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("keys", [])
    except Exception as e:
        print(f"⚠️  Warning: failed to load existing JWKS ({path}): {e}")
        return []


def save_jwks(path: Path, keys: List[dict]):
    """Write JWKS file."""
    with open(path, "w") as f:
        json.dump({"keys": keys}, f, indent=2)
    print(f"✅ JWKS written to {path} with {len(keys)} key(s)")


def rotate_jwks(keys: List[dict], new_key: dict, max_keys: int) -> List[dict]:
    """Append a new key and enforce max key count."""
    if new_key["kid"] in [k.get("kid") for k in keys]:
        print(f"ℹ️  Key with kid={new_key['kid']} already exists. No changes made.")
        return keys

    keys.append(new_key)
    print(f"➕ Added new key (kid={new_key['kid']})")

    if max_keys > 0 and len(keys) > max_keys:
        dropped = len(keys) - max_keys
        keys = keys[-max_keys:]
        print(f"♻️  Rotation: dropped {dropped} oldest key(s)")

    return keys


def revoke_key(keys: List[dict], kid: str) -> List[dict]:
    """Mark a key as revoked."""
    found = False
    for key in keys:
        if key.get("kid") == kid:
            key["use"] = "revoked"
            key["revoked_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            print(f"🚫 Revoked key with kid={kid}")
    if not found:
        print(f"⚠️  No key with kid={kid} found in JWKS.")
    return keys


def main():
    parser = argparse.ArgumentParser(description="Manage Tendril JWKS (generate, rotate, revoke)")
    parser.add_argument("--public-key", help="Path to PEM public key for adding a new key")
    parser.add_argument("--kid", help="Key ID for new key or revoke target")
    parser.add_argument("--output", required=True, help="Path to JWKS JSON file")
    parser.add_argument("--max-keys", type=int, default=0, help="Max number of keys to retain (0 = unlimited)")
    parser.add_argument("--revoke-kid", help="Revoke an existing key by KID")
    args = parser.parse_args()

    jwks_path = Path(args.output)
    keys = load_existing_jwks(jwks_path)

    if args.revoke_kid:
        # Revocation mode
        keys = revoke_key(keys, args.revoke_kid)
        save_jwks(jwks_path, keys)
        return

    if not args.public_key or not args.kid:
        parser.error("Must specify --public-key and --kid when not using --revoke-kid")

    new_key = generate_jwk(args.public_key, args.kid)
    keys = rotate_jwks(keys, new_key, args.max_keys)
    save_jwks(jwks_path, keys)


if __name__ == "__main__":
    main()
