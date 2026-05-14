# Central ThingsBoard CE server

Phase 2: the central ThingsBoard server that the edge device's `tb-edge`
instance synchronizes with.

```
PC (this host)                              Edge 192.168.8.175
┌──────────────────────────────┐           ┌─────────────────────────┐
│ gw-thingsboard               │           │ tb-edge-v2 container    │
│   :8080  UI / REST / metrics  │◀──RPC─────┤   CLOUD_RPC_HOST=PC     │
│   :7070  edge RPC             │   7070    │   CLOUD_RPC_PORT=7070   │
│   :1883  MQTT                 │           │   CLOUD_ROUTING_KEY=... │
│ gw-tb-postgres (in-memory Q)  │           │ tb-edge-postgres        │
└──────────────────────────────┘           └─────────────────────────┘
```

- Image `thingsboard/tb-node:4.3.1.1` — version-matched to the edge's
  `tb-edge:4.3.1.1EDGE`.
- Queue: **in-memory** (single-node, no Kafka — keeps RAM footprint ~1.7 GB).
- Prometheus metrics exposed at `:8080/actuator/prometheus`
  (`METRICS_ENABLED=true`, `METRICS_ENDPOINTS_EXPOSE=prometheus`).

## First run

```sh
cd services/thingsboard

# 1. Schema install — ONCE, before the first `up`. Container exits when done.
docker compose run --rm -e INSTALL_TB=true thingsboard-ce

# 2. Start
docker compose up -d

# 3. Open http://localhost:8080
#    Default sysadmin login: sysadmin / sysadmin  ->  change immediately.
```

First boot takes a few minutes (JVM warmup + DB migration).

## Connecting the edge device

1. Log into the central UI as a **tenant admin** (create a tenant under
   sysadmin first if needed).
2. **Edge management > Edges > +** — create an Edge instance. ThingsBoard
   generates a **routing key** and **routing secret**.
3. Put those into `secrets/tb-edge-cloud.env` (gitignored) and apply them to
   the edge device's `tb-edge` container — see [services/tb-edge/](../tb-edge/).

## Operations

```sh
docker compose ps
docker compose logs -f thingsboard-ce
docker compose down            # stop, keep data
docker compose down -v         # stop + WIPE postgres (full reset)
```

Data persists in `gw-tb-postgres-data`, `gw-tb-data`, `gw-tb-logs`.

## Notes

- This diverges from the `Tesis-app` reference compose, which used Kafka. For
  a single central node serving one edge, the in-memory queue is sufficient
  and saves ~1 GB RAM. Switch to Kafka only if scaling to multiple TB nodes.
- `JAVA_OPTS` is capped at `-Xmx1g` because the PC runs this alongside the
  observability stack and other workloads. Bump it if TB feels sluggish and
  RAM allows.
