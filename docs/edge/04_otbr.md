# 04 — OpenThread Border Router (OTBR)

The edge ships a working OTBR stack (`openthread-br 1.0-1`) but is **not
currently joined to a Thread network** — it has the daemons running, an
802.15.4 interface up, and a default mesh-local prefix, but no active dataset.

## Live state

```
$ ot-ctl state
detached
Done

$ ot-ctl ifconfig
up
Done

$ ot-ctl dataset active
Error 23: NotFound
```

`detached + ifconfig up + dataset NotFound` means: radio is initialized, no
network credentials are loaded, so the router can't attach. This is the
expected state for a freshly flashed edge that hasn't been commissioned yet.

## wpan0 interface

```
wpan0  UNKNOWN  fdf1:a391:6243:2a67:f820:9a70:166c:5f53/64
                fdde:ad00:beef:0:f820:9a70:166c:5f53/64
                fe80::2414:cf26:3d2c:19e7/64
```

The `fdde:ad00:beef::/64` prefix is OpenThread's stock mesh-local default
(used until a real dataset is committed). The other ULA prefix
(`fdf1:a391:6243:2a67::/64`) suggests a previous commissioning attempt
that left routes behind.

## Daemons

All four OTBR services are **enabled** in `/etc/init.d`:

| Service | Role |
|---|---|
| `otbr-agent` | Main daemon — talks to RCP, exposes `ot-ctl` API |
| `otbr-firewall` | Adds Thread-specific firewall rules |
| `otbr-srp` | mDNS / SRP advertiser for Thread service discovery |
| `otbr-addr-guard` | Guards against duplicate IPv6 addresses across mesh |

## Persisted config

```
/etc/config/otbr-agent
/etc/config/otbr-agent.bak.20260505-115110     # ← previous version
/etc/config/otbr-agent.bak.20260506-081106     # ← previous version
/etc/config/otbr-network
/etc/config/otbr-srp
```

Two timestamped backups indicate the OTBR config was last touched around
**May 5–6, 2026**. Worth diffing these to recover the previous Thread
credentials if commissioning needs to be resumed instead of restarted.

## Commissioning options (when ready)

Three paths to bring the OTBR into an operational Thread network, in order
of preference for this project:

### Option A — create a fresh Thread network on the edge

```
ot-ctl dataset init new
ot-ctl dataset networkname Gateway-SmartGrid
ot-ctl dataset channel 25            # decide based on RF survey, not default
ot-ctl dataset commit active
ot-ctl ifconfig up
ot-ctl thread start
```

Then export the dataset (`ot-ctl dataset active -x`) and provision Thread
end-devices with the same dataset.

The MCP exposes this as one shot:
- `mcp__edge__openwrt_thread_create_network`
- `mcp__edge__openwrt_thread_get_dataset` (read back to share)

### Option B — restore a previous dataset from backup

```
diff /etc/config/otbr-agent /etc/config/otbr-agent.bak.20260506-081106
# if the backup has a usable dataset, copy it back and restart otbr-agent
```

### Option C — join an existing Thread network (commissioner-driven)

Use the steering data / PSKd flow from another already-running OTBR.
MCP tool: `mcp__edge__openwrt_thread_enable_commissioner`.

## Open questions

- Which **PAN channel** is the deployment going to standardize on? Default
  is channel 11 (2405 MHz); local 2.4 GHz Wi-Fi will overlap unless we plan
  it.
- Is there an upstream **Thread border router peer** somewhere that this
  edge should mesh-link with, or is this edge meant to be the leader for a
  new mesh per site?
- Do we want **SRP service registration** advertised over mDNS only on the
  LAN, or proxied to the WAN? Affects `otbr-srp` config.
