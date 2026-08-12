#!/bin/bash
# Constant CoAP-over-6LoWPAN traffic generator.
# The OTBR acts as a CoAP client and GETs a node's resource in a loop, so the
# mesh always carries application-layer (CoAP/UDP/6LoWPAN/802.15.4) traffic.
#
# Target address is read from /home/sebas/coap_target.addr (written by
# setup_coap_a.sh). Tune with env: COAP_URI (default sensor), COAP_INTERVAL (s).
OT=/usr/sbin/ot-ctl
ADDR="$(cat /home/sebas/coap_target.addr 2>/dev/null)"
URI="${COAP_URI:-sensor}"
INTERVAL="${COAP_INTERVAL:-1}"

[ -z "$ADDR" ] && { echo "coap_constant: no target in /home/sebas/coap_target.addr"; exit 1; }

$OT coap start >/dev/null 2>&1
echo "coap_constant: GET coap://[$ADDR]/$URI every ${INTERVAL}s"
while true; do
  $OT coap get "$ADDR" "$URI" >/dev/null 2>&1
  sleep "$INTERVAL"
done
