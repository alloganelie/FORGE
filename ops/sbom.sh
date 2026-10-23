#!/bin/sh
# Produit une SBOM SPDX de l'image (ET-009). Necessite syft.
set -eu
image="${1:-forge-agent:local}"
output="${2:-build/sbom.spdx.json}"
mkdir -p "$(dirname "$output")"
if ! command -v syft >/dev/null 2>&1; then
  echo "syft absent : installer https://github.com/anchore/syft" >&2
  exit 1
fi
syft "$image" -o spdx-json > "$output"
echo "SBOM ecrite : $output"
