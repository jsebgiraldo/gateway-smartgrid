#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWRT="$ROOT/repos/openwrt-morse"

if [ ! -d "$OWRT" ]; then
  echo "ERROR: $OWRT not found. Run scripts/bootstrap.sh first." >&2
  exit 1
fi

cd "$OWRT"

echo "==> OpenWRT feeds update / install"
./scripts/feeds update -a
./scripts/feeds install -a

cat <<'EOF'

Feeds done. Next steps (MorseMicro HaLow):

  cd repos/openwrt-morse
  ./scripts/morse_setup.sh          # interactive target selection
  make defconfig
  make -j$(nproc)

EOF
