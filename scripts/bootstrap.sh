#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> git submodule update --init --recursive"
git submodule update --init --recursive

echo "==> Component-specific bootstrap"
"$ROOT/scripts/bootstrap-firmware.sh" || echo "WARN: firmware bootstrap failed (continuing)"
"$ROOT/scripts/bootstrap-openwrt.sh"  || echo "WARN: openwrt bootstrap failed (continuing)"

cat <<'EOF'

Bootstrap done. Per-component build instructions live in each submodule's README:

  repos/firmware-ami-lwm2m   Zephyr LwM2M client     (west build)
  repos/openwrt-morse        OpenWRT (HaLow fork)    (make -j$(nproc))
  repos/flash-tool           Next.js flasher         (npm install && npm run dev)
  repos/mcp-openwrt-ssh      Python MCP server       (pip install .)

EOF
