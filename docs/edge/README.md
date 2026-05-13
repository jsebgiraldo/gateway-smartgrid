# Edge Gateway — Operational Baseline

Snapshot of the production edge device taken **2026-05-13** via `mcp__edge` / direct SSH.
Use this as the reference for every change going forward: any divergence from these
files should arrive via a PR that explains what changed and why.

## Device

| Field | Value |
|---|---|
| Hostname | `r1000-wm6108-a3dd` |
| Model | Seeed reComputer R1000 (Morse Micro WM6108-SPI) |
| SoC | Broadcom BCM2711 (CM4), 4× Cortex-A72 |
| OS | OpenWrt 23.05.5 Morse-2.9-dev (kernel 5.15.167 aarch64) |
| Management IP | 192.168.8.175 (WAN, DHCP from upstream router) |
| LAN subnet | 10.42.0.0/24 (br-lan, `r1000-wm6108-a3dd` AP) |
| Timezone | America/Bogota (`<-05>5`) |

## Contents

| Doc | Scope |
|---|---|
| [01_system.md](01_system.md) | Hardware, OS, kernel, CPU, memory, storage |
| [02_network.md](02_network.md) | Interfaces, routes, IPv6, firewall, DHCP, dnsmasq |
| [03_wireless.md](03_wireless.md) | radio0 (Morse HaLow S1G) + radio1 (5 GHz mac80211) |
| [04_otbr.md](04_otbr.md) | OpenThread Border Router state and configuration |
| [05_docker.md](05_docker.md) | Containerized workloads (ThingsBoard Edge + Postgres) |
| [06_services.md](06_services.md) | Enabled init.d services, processes, daemons |

## Standing issues (as of snapshot)

- **Storage at 94 %**: `/` rootfs has 468 MB free of 7.4 GB. ThingsBoard postgres
  data lives here; needs sizing decision before any data growth.
- **OTBR not joined to a Thread network**: `ot-ctl dataset active` returns
  `Error 23: NotFound`. `otbr-agent` is up and `wpan0` is up, but no active
  dataset has been provisioned. See [04_otbr.md](04_otbr.md).
- **No wireless clients**: both radios are AP/up, 0 stations associated on
  either HaLow or 5 GHz.

## How this baseline was captured

Single SSH session via `docker run --rm --network host openwrt-ssh-mcp:latest`
executing ~40 read-only commands serially (`ubus`, `uci show`, `ip`, `iptables`,
`docker ps`, `ot-ctl`, `ps`, `opkg list-installed | grep`). Raw output is in
[`../../logs/`](../../logs/) (gitignored) for traceability.

To refresh this baseline after material changes:

```sh
# from orchestrator root
docker run --rm --network host --env-file secrets/edge.env \
  --entrypoint sh openwrt-ssh-mcp:latest -c '...inventory script...'
```

Re-run inventory and PR the diffs against `docs/edge/`.
