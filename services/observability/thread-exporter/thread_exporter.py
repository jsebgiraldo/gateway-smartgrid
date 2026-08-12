#!/usr/bin/env python3
"""
OpenThread / IEEE 802.15.4 metrics exporter for Prometheus.

Runs `ot-ctl` against the local OTBR (otbr-agent) and exposes OpenThread
counters + topology as Prometheus metrics, grouped by OSI layer:

  L1 PHY   : neighbor RSSI / LQI, channel, CCA failures (TxErrBusyChannel)
  L2 MAC   : 802.15.4 frame Tx/Rx, ACK ratio, retries, FCS (CRC) errors
  L3 NET   : MLE role / partition changes, time-in-role, IPv6 pkt success/fail
  Topology : router / child / neighbor counts

Metrics are collected fresh on every Prometheus scrape.
Serves /metrics on :9101.

Requires: python3-prometheus-client, and passwordless `sudo ot-ctl`
(otbr-agent installs ot-ctl in /usr/sbin).
"""
import os
import re
import subprocess

from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

OT_CTL = os.environ.get("OT_CTL", "sudo ot-ctl").split()
LISTEN_PORT = int(os.environ.get("THREAD_EXPORTER_PORT", "9101"))
ROLE_MAP = {"disabled": 0, "detached": 1, "child": 2, "router": 3, "leader": 4}


def ot(*args, timeout=6):
    """Run one ot-ctl command; return output lines minus 'Done'/'Error'/blank."""
    try:
        out = subprocess.run(OT_CTL + list(args), capture_output=True,
                             text=True, timeout=timeout).stdout
    except Exception:
        return []
    lines = []
    for ln in out.replace("\r", "").splitlines():
        s = ln.strip()
        if s and s != "Done" and not s.startswith("Error"):
            lines.append(ln.rstrip())
    return lines


def parse_counters(lines):
    """Parse 'Name: value' lines (indented sub-counters allowed) into a dict."""
    d = {}
    for ln in lines:
        m = re.match(r"\s*([A-Za-z0-9 _]+):\s*(\d+)\s*$", ln)
        if m:
            d[m.group(1).strip()] = int(m.group(2))
    return d


def first(lines, default=""):
    return lines[0].strip() if lines else default


# name in ot-ctl -> (prom metric name, help)
MAC_MAP = {
    "TxTotal": ("thread_mac_tx_frames_total", "802.15.4 MAC frames transmitted"),
    "TxUnicast": ("thread_mac_tx_unicast_total", "MAC unicast frames transmitted"),
    "TxBroadcast": ("thread_mac_tx_broadcast_total", "MAC broadcast frames transmitted"),
    "TxAckRequested": ("thread_mac_tx_ack_requested_total", "MAC TX frames that requested an ACK"),
    "TxAcked": ("thread_mac_tx_acked_total", "MAC TX frames successfully acknowledged"),
    "TxData": ("thread_mac_tx_data_total", "MAC data frames transmitted"),
    "TxRetry": ("thread_mac_tx_retry_total", "MAC TX retries"),
    "TxErrCca": ("thread_mac_tx_err_cca_total", "MAC TX CCA (clear-channel-assessment) failures"),
    "TxErrBusyChannel": ("thread_mac_tx_err_busy_channel_total", "MAC TX aborted because channel was busy"),
    "TxErrAbort": ("thread_mac_tx_err_abort_total", "MAC TX aborted"),
    "TxDirectMaxRetryExpiry": ("thread_mac_tx_direct_max_retry_expiry_total", "Direct MAC TX max-retry expiries"),
    "RxTotal": ("thread_mac_rx_frames_total", "802.15.4 MAC frames received"),
    "RxUnicast": ("thread_mac_rx_unicast_total", "MAC unicast frames received"),
    "RxBroadcast": ("thread_mac_rx_broadcast_total", "MAC broadcast frames received"),
    "RxData": ("thread_mac_rx_data_total", "MAC data frames received"),
    "RxErrFcs": ("thread_mac_rx_err_fcs_total", "MAC RX FCS/CRC errors"),
    "RxErrSec": ("thread_mac_rx_err_sec_total", "MAC RX security errors"),
    "RxErrNoFrame": ("thread_mac_rx_err_no_frame_total", "MAC RX no-frame errors"),
    "RxDuplicated": ("thread_mac_rx_duplicated_total", "MAC RX duplicated frames"),
}
IP_MAP = {
    "TxSuccess": ("thread_ip_tx_success_total", "IPv6 packets transmitted OK"),
    "TxFailed": ("thread_ip_tx_failed_total", "IPv6 packets failed to transmit"),
    "RxSuccess": ("thread_ip_rx_success_total", "IPv6 packets received OK"),
    "RxFailed": ("thread_ip_rx_failed_total", "IPv6 packets failed to receive"),
}
MLE_TIME = {"Time Disabled Milli": "disabled", "Time Detached Milli": "detached",
            "Time Child Milli": "child", "Time Router Milli": "router",
            "Time Leader Milli": "leader"}


class ThreadCollector(object):
    def collect(self):
        netname = first(ot("networkname"))
        try:
            channel = int(first(ot("channel"), "0"))
        except ValueError:
            channel = 0
        state = first(ot("state"), "unknown").lower()
        lbl = [netname]

        # --- identity / topology gauges ---
        g = GaugeMetricFamily("thread_node_role",
                              "Current role: 0=disabled 1=detached 2=child 3=router 4=leader",
                              labels=["network"])
        g.add_metric(lbl, ROLE_MAP.get(state, -1))
        yield g

        g = GaugeMetricFamily("thread_channel", "802.15.4 channel currently in use", labels=["network"])
        g.add_metric(lbl, channel)
        yield g

        try:
            pid = int(first(ot("partitionid"), "0"))
            g = GaugeMetricFamily("thread_partition_id", "Thread partition id", labels=["network"])
            g.add_metric(lbl, pid)
            yield g
        except ValueError:
            pass

        # --- L2 MAC counters ---
        mac = parse_counters(ot("counters", "mac"))
        for k, (name, help_) in MAC_MAP.items():
            if k in mac:
                c = CounterMetricFamily(name, help_, labels=["network"])
                c.add_metric(lbl, mac[k])
                yield c

        # --- L3 MLE counters ---
        mle = parse_counters(ot("counters", "mle"))
        if "Partition Id Changes" in mle:
            c = CounterMetricFamily("thread_mle_partition_id_changes_total",
                                    "MLE partition-id changes", labels=["network"])
            c.add_metric(lbl, mle["Partition Id Changes"])
            yield c
        if "Parent Changes" in mle:
            c = CounterMetricFamily("thread_mle_parent_changes_total",
                                    "MLE parent changes", labels=["network"])
            c.add_metric(lbl, mle["Parent Changes"])
            yield c
        trole = CounterMetricFamily("thread_mle_time_in_role_ms_total",
                                    "Cumulative time in each MLE role (ms)",
                                    labels=["network", "role"])
        for key, role in MLE_TIME.items():
            if key in mle:
                trole.add_metric([netname, role], mle[key])
        yield trole

        # --- IPv6 counters ---
        ip = parse_counters(ot("counters", "ip"))
        for k, (name, help_) in IP_MAP.items():
            if k in ip:
                c = CounterMetricFamily(name, help_, labels=["network"])
                c.add_metric(lbl, ip[k])
                yield c

        # --- L1 PHY: per-neighbor RSSI / LQI ---
        rssi = GaugeMetricFamily("thread_neighbor_avg_rssi_dbm", "Neighbor average RSSI (dBm)",
                                 labels=["network", "rloc16", "extaddr"])
        lqi = GaugeMetricFamily("thread_neighbor_lqi_in", "Neighbor incoming link quality (0-3)",
                                labels=["network", "rloc16", "extaddr"])
        n = 0
        for ln in ot("neighbor", "table"):
            cols = [c.strip() for c in ln.split("|")]
            # ['', Role, RLOC16, Age, AvgRSSI, LastRSSI, LQIn, R, D, N, ExtMAC, Ver, '']
            if len(cols) >= 12 and cols[2].startswith("0x"):
                try:
                    rssi.add_metric([netname, cols[2], cols[10]], float(cols[4]))
                    lqi.add_metric([netname, cols[2], cols[10]], float(cols[6]))
                    n += 1
                except ValueError:
                    pass
        yield rssi
        yield lqi
        g = GaugeMetricFamily("thread_neighbor_count", "Number of direct radio neighbors", labels=["network"])
        g.add_metric(lbl, n)
        yield g

        # --- Topology counts ---
        rcount = sum(1 for ln in ot("router", "table") if re.search(r"\|\s*0x[0-9a-fA-F]{4}\s*\|", ln))
        g = GaugeMetricFamily("thread_router_count", "Routers in the partition", labels=["network"])
        g.add_metric(lbl, rcount)
        yield g
        ccount = sum(1 for ln in ot("child", "table") if re.search(r"\|\s*0x[0-9a-fA-F]{4}\s*\|", ln))
        g = GaugeMetricFamily("thread_child_count", "Children of this node", labels=["network"])
        g.add_metric(lbl, ccount)
        yield g

        g = GaugeMetricFamily("thread_up", "1 if ot-ctl responded this scrape", labels=["network"])
        g.add_metric(lbl, 1 if netname else 0)
        yield g


if __name__ == "__main__":
    REGISTRY.register(ThreadCollector())
    start_http_server(LISTEN_PORT)
    print("thread-exporter listening on :%d/metrics" % LISTEN_PORT, flush=True)
    import time
    while True:
        time.sleep(3600)
