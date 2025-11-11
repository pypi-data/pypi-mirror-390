# Tendril JWT Infrastructure (`tendril.jwt`)

This package implements **secure JWT signing, verification, and key management** for the Tendril framework and compatible applications.

It provides a minimal, flexible core for issuing and validating **per-domain JWTs**, each of which can define its own claims, audience, and lifetime — suitable for both internal service authentication and downstream integration with third-party systems (e.g., Grafana, devices, or external APIs).

---

## 🔩 Overview

The `tendril.jwt` package is responsible for:

* Managing RSA keypairs and JWKS (JSON Web Key Sets)
* Generating signed JWTs with per-domain claim specifications
* Verifying incoming tokens against the JWKS
* Handling rotation and revocation of keys cleanly
* Providing domain registration for per-application authorization flows

It’s designed to work both **stand-alone** and **integrated within Tendril’s authentication system** (`tendril.authn` and `tendril.authz`).

---

## 📦 Package layout

```
tendril/jwt/
├── __init__.py
├── secrets.py       # Key and JWKS loader
├── common.py        # Domain registry + utility functions
├── signer.py        # JWT generation and signing
├── verify.py        # JWT validation and public-key selection
└── utils_async.py   # Helpers for async/sync-safe callables
```

---

## ⚙️ Application responsibilities

An application using `tendril.jwt` **must provide**:

1. **Configuration values** (typically in `tendril.config`):

   ```python
   AUTH_JWKS_PATH = "~/.tendril/jwt/jwks.json"
   AUTH_JWT_PRIVATE_KEY = "~/.tendril/jwt/privateKey.pem"
   AUTH_JWT_PUBLIC_KEY = "~/.tendril/jwt/publicKey.pem"
   AUTH_JWT_ISSUER = "https://your-app.example.com"
   AUTH_JWT_VALIDITY = 3600  # seconds
   AUTH_JWT_TTL = 5          # seconds of not-before offset
   AUTH_JWT_ALGORITHMS = ["RS256"]
   ```

2. **Key material**, created using the provided scripts (see below).
   These live under `~/.tendril/jwt/` by default.

3. **Domain registration** — each JWT domain corresponds to a specific integration or service.

   ```python
   from tendril.jwt.common import register_domain
   from tendril.authz.domains.base import AuthzDomainBase

   class GrafanaAuthzDomain(AuthzDomainBase):
       jwt_spec = {"claims": {"sub": "user.email"}}
       def get_audience(self):
           return "grafana"

   register_domain("grafana", GrafanaAuthzDomain())
   ```

---

## 🔐 Key management

Tendril provides two shell utilities for managing cryptographic keys:

### 1. Install system prerequisites

```bash
./install_jwt_prereqs.sh
```

This installs `openssl` and (optionally) `jq` — no Python dependencies.

### 2. Generate or rotate keys

```bash
./generate_tendril_jwt_keys.sh
```

This script:

* Creates a new RSA keypair (`privateKey.pem`, `publicKey.pem`)
* Computes a short `kid` hash
* Adds or rotates keys in `jwks.json`
* Applies correct permissions (`600` for private key, `644` for others)

You can limit retained keys:

```bash
MAX_KEYS=3 ./generate_tendril_jwt_keys.sh
```

### 3. Revoke a compromised key

```bash
python3 generate_jwks.py --revoke-kid <kid> --output ~/.tendril/jwt/jwks.json
```

Revoked keys are marked:

```json
{
  "use": "revoked",
  "revoked_at": "2025-11-02T12:34:56.789012+00:00"
}
```

---

## ✍️ Signing JWTs

Tokens are generated per-domain:

```python
from tendril.jwt.signer import generate_token

token = generate_token(domain_name="grafana", user=current_user)
print(token)
```

Each domain defines its own `jwt_spec`, such as:

```python
jwt_spec = {
    "claims": {
        "sub": "user.email",
        "org": "user.organization_id",
    },
    "validity": 3600,
    "ttl": 5
}
```

Claims are resolved dynamically:

* `"user.email"` → uses `context["user"].email`
* If callable, it’s invoked as `context["user"].method(context)`
* Async callables are automatically awaited

---

## 🧾 Verifying JWTs

Verification validates signature, issuer, and audience:

```python
from tendril.jwt.verify import verify_jwt

payload = verify_jwt(token)
print(payload["sub"])
```

The verifier automatically:

* Loads the JWKS (`tendril.jwt.secrets.jwks`)
* Selects the correct key based on `kid`
* Rejects revoked keys
* Validates expiry, nbf, and signature

---

## 🧩 How Tendril uses it

Within **Tendril**, the JWT layer is used for multiple purposes:

| Use case                    | Description                                                                                                             |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Frontend ↔ Backend auth** | The frontend authenticates through Stytch (or Auth0), and Tendril issues a secondary JWT scoped to backend APIs.        |
| **Device authentication**   | Registered devices receive their own credentials and use password flow → backend issues JWTs for secured communication. |
| **Integration domains**     | Certain services (e.g., Grafana, Prometheus) use per-domain JWTs generated from Tendril’s authorization logic.          |

Each of these uses the same core primitives — a domain registration with a custom `jwt_spec`, and `generate_token()` to issue domain-specific credentials.

---

## 🧠 Key design points

* Minimal core with clear boundaries: key storage, signing, verification, and domain logic are all separate.
* Fully async-safe token generation (`generate_token_async()` available).
* JWKS supports **rotation** and **revocation** out-of-the-box.
* Tests cover key loading, domain registry, signer, verifier, and utils.

---

## 🧪 Tests

Run all JWT tests:

```bash
pytest -v tests/test_jwt_*.py
```

This includes:

* `test_secrets.py`
* `test_common.py`
* `test_signer.py`
* `test_verify.py`
* `test_utils_async.py`

---

## 📚 Summary

| Component                      | Responsibility                           |
| ------------------------------ | ---------------------------------------- |
| `secrets.py`                   | Load RSA keys and JWKS                   |
| `common.py`                    | Domain registry and UTC utility          |
| `signer.py`                    | Create JWTs from registered domain specs |
| `verify.py`                    | Validate incoming tokens                 |
| `generate_jwks.py`             | Manage and rotate JWKS keys              |
| `generate_tendril_jwt_keys.sh` | Generate initial key material            |

---

**Tendril JWT** is a focused, minimal, auditable core for modern JWT workflows.
It unifies user, device, and service authentication across Tendril deployments, while 
allowing per-domain extensibility and clean key lifecycle management.
