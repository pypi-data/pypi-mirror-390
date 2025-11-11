#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------
# Tendril JWT Key Generator
# ---------------------------------------------------------------------
# Generates RSA private/public keypair and JWKS metadata.
# Requires:
#   - openssl (installed via install_jwt_prereqs.sh)
#   - generate_jwks.py (Python helper in same directory)
# ---------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANCE_ROOT="${HOME}/.tendril"
JWT_DIR="${INSTANCE_ROOT}/jwt"

PRIVATE_KEY="${JWT_DIR}/privateKey.pem"
PUBLIC_KEY="${JWT_DIR}/publicKey.pem"
JWKS_FILE="${JWT_DIR}/jwks.json"

mkdir -p "${JWT_DIR}"

echo "🔐 Generating Tendril JWT keypair..."
echo "   Output directory: ${JWT_DIR}"

# 1️⃣ Generate 4096-bit RSA private key
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out "${PRIVATE_KEY}"

# 2️⃣ Extract the corresponding public key
openssl rsa -in "${PRIVATE_KEY}" -pubout -out "${PUBLIC_KEY}"

# 3️⃣ Compute a simple KID (hash of public key)
KID=$(openssl rsa -in "${PRIVATE_KEY}" -pubout 2>/dev/null | openssl sha256 | awk '{print $2}' | cut -c1-16)

# 4️⃣ Build JWKS via Python helper
echo "🧩 Generating JWKS using generate_jwks.py..."
python3 "${SCRIPT_DIR}/generate_jwks.py" \
  --public-key "${PUBLIC_KEY}" \
  --kid "${KID}" \
  --output "${JWKS_FILE}"

# 5️⃣ Secure permissions
chmod 600 "${PRIVATE_KEY}"
chmod 644 "${PUBLIC_KEY}" "${JWKS_FILE}"

echo
echo "✅ JWT key generation complete."
echo "   Private key : ${PRIVATE_KEY}"
echo "   Public key  : ${PUBLIC_KEY}"
echo "   JWKS file   : ${JWKS_FILE}"
echo "   Key ID (kid): ${KID}"
echo
echo "You can now set your Tendril config to:"
echo
echo "  AUTH_JWT_PRIVATE_KEY=${PRIVATE_KEY}"
echo "  AUTH_JWT_PUBLIC_KEY=${PUBLIC_KEY}"
echo "  AUTH_JWKS_PATH=${JWKS_FILE}"
echo
echo "🔁 To rotate keys, rerun this script. A new KID will be assigned."
