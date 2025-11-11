#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------
# Tendril JWT System Prerequisites Installer
#
# This script installs only system-level dependencies required
# for key generation and management.
# Python dependencies are *not* installed here — they belong
# in your virtualenv or setup.py.
# ---------------------------------------------------------------------

echo "🔧 Installing Tendril JWT system prerequisites..."

sudo apt-get update -qq

# Required: OpenSSL for keypair generation
sudo apt-get install -y openssl

# Optional: jq for inspecting JSON JWKS files
if ! command -v jq &>/dev/null; then
  echo "🔹 Installing jq (optional, useful for inspecting JWKS)"
  sudo apt-get install -y jq
fi

echo "✅ System prerequisites installed successfully."
