# 07 — Edge Memory Budget

The Seeed R1000 edge has **1.85 GB total RAM and no swap** (see
[01_system.md](01_system.md), and the swap saga in chat history — kmod-zram
is absent from the Morse firmware and overlayfs rejects swapfiles). Capacity
planning has to be done explicitly, not discovered under load.

This document fixes the per-component budget and the headroom available
for adding LwM2M / Thread devices.

## Measured baseline  (snapshot taken 2026-05-16, idle / 2 ESP32 rejected)

All values are MB unless noted. Captured from Prometheus at the time of
writing — see [Gateway Overview dashboard](../../services/observability/grafana/dashboards/gateway-overview.json)
for the live numbers.

| Metric | Value | Notes |
|---|---|---|
| `MemTotal` | 1 805 | What the kernel sees |
| `MemAvailable` | 470 | Real "free for new allocations" |
| `MemFree` | 73 | Hard-free (rest is in cache/buffers) |
| Buffers + Cached + Slab | 570 | Reclaimable under pressure |
| **`Committed_AS`** | **1 856** | Processes have *promised* memory > total — overcommit territory |
| `CommitLimit` | ~ 900 | swap + (RAM × overcommit_ratio); we're 2× over |
| `tb-edge` JVM RSS | 805 | heap committed (499) + non-heap (306) |
| `tb-edge` JVM heap used | 276 | Only ~ 56 % of the 499 MB committed |
| `tb-edge` JVM threads | 223 live | TB is thread-heavy |
| Postgres on edge (tb-edge-postgres) | ~ 170 (VSZ; RSS smaller) | from earlier `ps` |

## Budget — what the edge spends RAM on

| Component | Reserved (MB) | Measured today (MB) | Comment |
|---|---|---|---|
| OpenWrt base + system services (procd, dropbear, dnsmasq, otbr-agent, dockerd, hostapd × 2, mediamtx-disabled, …) | **350** | ~ 350 (residual after tb-edge + postgres) | "everything else"; trimmed 4 services already, no big lever left |
| **`tb-edge` JVM**  (`-Xmx768m` configured) | **900** | 805 | heap can grow to 768 MB committed; +overhead → ~ 900 MB hard ceiling |
| Postgres (`tb-edge-postgres`) | **200** | ~ 170 | mostly `shared_buffers` (128 MB default) + connection memory |
| Page cache + buffers + slab | **300** (reclaimable, soft) | 570 | kernel uses what's free; reclaimed under pressure |
| **Headroom for new devices + spikes** | **~ 250** | — | this is the real ceiling for adding LwM2M / Thread devices |
| **Total** | **2 000** | — | already exceeds physical 1 805 MB → relies on cache reclaim + overcommit |

The budget already assumes the cache is reclaimable. Under real LwM2M load
the kernel will shrink the cache before it OOM-kills anything — so the
effective working ceiling is **~ 470 MB available** = the headroom column.

## Per-device cost (estimates from measured baseline)

Each LwM2M device on tb-edge adds, roughly:
- **JVM heap**: ~ 2–5 MB (DTLS session + CoAP observes + device actor + rule engine state)
- **Postgres**: ~ 100–500 KB (device row + recent telemetry rows)
- **CPU**: rule engine + transport work scaling with telemetry rate

Working math: 250 MB headroom ÷ 3 MB/device ≈ **~ 80 devices theoretical**,
**~ 25–40 comfortable** with GC pressure and a real safety margin in mind.

Thread devices on OTBR — basically zero edge-side RAM cost. The 802.15.4
mesh state is microscopic. The cost arrives only if their data is funneled
into tb-edge (then it's the LwM2M-equivalent budget).

## Hard rules this budget implies

1. **Do not push past ~ 30 LwM2M devices** without re-measuring first. The
   2-ESP32 baseline is not enough to extrapolate confidently to 50+.
2. **Do not raise `-Xmx`**: the JVM is already 805 / 900 MB of its reservation,
   and bumping `-Xmx` eats the headroom.
3. **Consider *lowering* `-Xmx` to 512m**: heap used is only 276 MB (56 % of
   committed). Lowering Xmx to 512m frees ~ 250 MB of headroom — see
   [#6 in chat] / the tuning to come.
4. **Postgres on the edge stays a candidate for relocation** (see
   [#5 evaluation] / the next doc). Moving postgres to the central PC
   frees ~ 170 MB on the edge.
5. **No new services on the edge** unless something else leaves. Every MB
   added to OpenWrt base subtracts from the device headroom.

## When this budget needs to be revisited

- After any change to `JAVA_OPTS` on tb-edge (re-measure heap committed at idle).
- After connecting ≥ 5 real LwM2M devices (the per-device cost is an estimate
  until we have data).
- After moving postgres off the edge (~ 170 MB returned to the budget).
- If RAM compression (zram) is ever built from the openwrt-morse source —
  zram effectively multiplies usable RAM ~ 2–3× under cache pressure.

## How to capture a fresh snapshot

Open the **Gateway Overview** dashboard, screenshot the top row (Edge OS, tb-edge JVM).
Or query directly:

```sh
curl -s "http://localhost:9090/api/v1/query?query=node_memory_MemAvailable_bytes%7Bjob%3D%22edge-node%22%7D%2F1024%2F1024"
```
