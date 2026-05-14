# Observability stack — Prometheus + Grafana

Phase 1 of edge metrics: Prometheus scrapes the edge gateway's
`prometheus-node-exporter-lua`, Grafana visualizes it.

```
PC (this host)                              Edge 192.168.8.175
┌────────────────────────────┐             ┌────────────────────────┐
│ gw-prometheus :9090 ───────┼── scrape ──▶│ node-exporter-lua :9100│
│ gw-grafana    :3000        │             └────────────────────────┘
│   └─ datasource ▶ prom     │
└────────────────────────────┘
```

## Prerequisites

- Docker Desktop running on the PC.
- PC on the `192.168.8.0/24` LAN (same segment as the edge's WAN).
- Edge already provisioned with `prometheus-node-exporter-lua` listening on
  `192.168.8.175:9100` and a firewall rule allowing the LAN subnet. See
  [../../docs/edge/](../../docs/edge/) — this was done during Phase 1 setup.

## First run

```sh
# 1. Credentials (one time)
cp services/observability/.env.example secrets/observability.env
#    edit secrets/observability.env — change GF_SECURITY_ADMIN_PASSWORD

# 2. Start
cd services/observability
docker compose up -d

# 3. Open
#    Prometheus  http://localhost:9090   (Status > Targets — edge-node should be UP)
#    Grafana     http://localhost:3000   (login with secrets/observability.env creds)
```

Grafana auto-provisions:
- **Datasource** `Prometheus` (default, points at the prometheus container).
- **Dashboard** "OpenWrt" under the *Edge Gateway* folder — Grafana dashboard
  [11147](https://grafana.com/grafana/dashboards/11147), tailored for
  `prometheus-node-exporter-lua`.

## Files

| Path | Purpose |
|---|---|
| `docker-compose.yml` | Prometheus + Grafana services |
| `prometheus/prometheus.yml` | Scrape targets (edge node-exporter) |
| `grafana/provisioning/datasources/prometheus.yml` | Auto-add Prometheus datasource |
| `grafana/provisioning/dashboards/provider.yml` | Auto-load dashboards from disk |
| `grafana/dashboards/openwrt-edge.json` | OpenWrt dashboard (11147, datasource refs rewritten to `Prometheus`) |
| `.env.example` | Template for `secrets/observability.env` |

## Adding scrape targets

Edit `prometheus/prometheus.yml`, then reload without restart:

```sh
curl -X POST http://localhost:9090/-/reload
```

Planned next targets (commented in `prometheus.yml`):
- `edge-tb-edge` — ThingsBoard Edge `/actuator/prometheus` endpoint.
- `router-node` — node-exporter on the GL-MT6000 router (192.168.8.1).

## Operations

```sh
docker compose ps                 # status
docker compose logs -f prometheus # tail logs
docker compose down               # stop (volumes persist)
docker compose down -v            # stop + wipe metrics history
```

Data persists in named volumes `gw-prometheus-data` (30-day retention) and
`gw-grafana-data`.

## Troubleshooting

- **Target `edge-node` DOWN in Prometheus**: from the PC run
  `curl http://192.168.8.175:9100/metrics`. If that fails, the edge firewall
  rule or the exporter service is the problem, not this stack.
- **Grafana dashboard empty**: confirm the datasource test passes
  (Connections > Data sources > Prometheus > Test) and that Prometheus has the
  `edge-node` target UP.
