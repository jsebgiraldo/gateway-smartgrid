#!/usr/bin/env bash
set -euo pipefail

# ami-lwm2m-node is a Zephyr APPLICATION (no west.yml of its own).
# It must live inside an NCS or upstream Zephyr workspace to build.
# Until the firmware repo ships its own west.yml, the workspace setup is manual.

if ! command -v west >/dev/null 2>&1; then
  echo "ERROR: 'west' not found. Install with: pip install west" >&2
  exit 1
fi

cat <<'EOF'
ami-lwm2m-node is a Zephyr app and does not yet ship a west.yml.
Manual setup (one-time, outside this repo tree):

  mkdir ~/zephyr-workspace && cd ~/zephyr-workspace
  west init -m https://github.com/nrfconnect/sdk-nrf --mr v2.6.0 ncs
  west update
  # then symlink or copy this orchestrator's repos/firmware-ami-lwm2m/ as the app

See: https://github.com/jsebgiraldo/ami-lwm2m-node#build
EOF
