#!/usr/bin/env bash
# Stub. Each component has its own build system; there is no single 'build all'
# command yet. This script just lists the per-component invocations.
set -euo pipefail

cat <<'EOF'
Build each component individually:

  repos/firmware-ami-lwm2m   west build -b <board>
  repos/openwrt-morse        make -j$(nproc)
  repos/flash-tool           npm install && npm run build
  repos/mcp-openwrt-ssh      pip install .

A unified build pipeline lives in .github/workflows/orchestrator-ci.yml.
EOF
