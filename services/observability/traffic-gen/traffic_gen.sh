#!/bin/bash
# Generate controlled IEEE 802.15.4 traffic from the OTBR to a mesh node and
# print the MAC-counter delta, to study channel usage / CCA / fragmentation.
#
#   baseline  : 20 x 32-byte pings   -> 1 MAC frame per packet (reference)
#   fragment  : 15 x 1000-byte pings -> 6LoWPAN fragments each into many frames
#   flood     : 80 x 64-byte pings, min interval -> saturates channel, CCA rises
#   multicast : 20 pings to ff03::1  -> every node (broadcast-style)
#
# Usage: bash traffic_gen.sh [baseline|fragment|flood|multicast]
OT="sudo ot-ctl"
MODE="${1:-baseline}"

mleid=$($OT ipaddr mleid | tr -d '\r' | head -1)
prefix=$(echo "$mleid" | cut -d: -f1-4)
rloc=$($OT neighbor table | tr -d '\r' | grep -oE '0x[0-9a-fA-F]{4}' | head -1)
target="${prefix}:0:ff:fe00:${rloc#0x}"

echo "Mesh-local prefix : ${prefix}::/64"
echo "Target node       : ${target}  (RLOC ${rloc})"
echo

before=$($OT counters mac | tr -d '\r')
tx0=$(echo "$before" | awk '/TxTotal:/{print $2}')
cca0=$(echo "$before" | awk '/TxErrCca:/{print $2}')
data0=$(echo "$before" | awk '/TxData:/{print $2}')

case "$MODE" in
  baseline)  echo ">> baseline: 20 x 32B"; $OT ping "$target" 32 20 1 ;;
  fragment)  echo ">> fragment: 15 x 1000B (6LoWPAN segmenta)"; $OT ping "$target" 1000 15 1 ;;
  flood)     echo ">> flood: 80 x 64B rapido (satura canal)"; $OT ping "$target" 64 80 1 hoplimit 64 ;;
  multicast) echo ">> multicast a ff03::1"; $OT ping ff03::1 32 20 1 ;;
  *) echo "modo desconocido: $MODE"; exit 1 ;;
esac

sleep 2
after=$($OT counters mac | tr -d '\r')
tx1=$(echo "$after" | awk '/TxTotal:/{print $2}')
cca1=$(echo "$after" | awk '/TxErrCca:/{print $2}')
data1=$(echo "$after" | awk '/TxData:/{print $2}')

echo
echo "=== delta MAC (efecto del trafico) ==="
echo "TxTotal frames           : +$((tx1 - tx0))"
echo "TxData  frames           : +$((data1 - data0))"
echo "TxErrCca (canal ocupado) : +$((cca1 - cca0))"
echo
echo "En Grafana veras subir: frames/s (uso del canal), y en 'fragment' el ratio frames/pkt (segmentacion)."
