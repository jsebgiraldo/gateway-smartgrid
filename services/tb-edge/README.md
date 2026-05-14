# ThingsBoard Edge (runs on the edge device)

This compose file is the **versioned, reproducible** definition of the
`tb-edge` deployment that runs on the edge device (192.168.8.175). It was
reconstructed from `docker inspect` of the pre-existing `docker run`
deployment so the edge stack can be managed via compose from now on.

## What changed vs. the original deployment

| Setting | Original (standalone) | Now (connected) |
|---|---|---|
| `CLOUD_RPC_HOST` | `127.0.0.1` | `192.168.8.124` (PC central) |
| `CLOUD_ROUTING_KEY` | `disabled` | real key from central Edge entity |
| `CLOUD_ROUTING_SECRET` | `disabled` | real secret |
| `METRICS_ENABLED` | (unset) | `true` |
| `METRICS_ENDPOINTS_EXPOSE` | (unset) | `prometheus` |

Everything else (transports, ports, local DB, JVM opts, bind mounts) is
identical to the original. The data bind mounts under
`/opt/docker/tb-edge-data` are reused — **no data loss** on recreate.

## Deploy / update on the edge

```sh
# from the orchestrator root, on the PC:
scp services/tb-edge/docker-compose.yml      root@192.168.8.175:/opt/docker/tb-edge/docker-compose.yml
scp secrets/tb-edge-cloud.env                root@192.168.8.175:/opt/docker/tb-edge/tb-edge-cloud.env

# on the edge:
ssh root@192.168.8.175
  cd /opt/docker/tb-edge
  docker compose up -d        # recreates tb-edge-v2 + tb-edge-postgres with new env
  docker compose logs -f tb-edge
```

Compose adopts the existing container names (`tb-edge-v2`,
`tb-edge-postgres`) and recreates them in place.

## Verify the edge connected to the central

- Central UI → Edge management → Edges → `edge-r1000-wm6108` should show
  **Active**.
- `docker compose logs tb-edge | grep -i cloud` on the edge — look for a
  successful RPC connection to `192.168.8.124:7070`.
- Prometheus target `edge-tb-edge` (192.168.8.175:8090) should go UP.

## Rollback to standalone

```sh
# on the edge, edit tb-edge-cloud.env:
CLOUD_RPC_HOST=127.0.0.1
CLOUD_ROUTING_KEY=disabled
CLOUD_ROUTING_SECRET=disabled
# then: docker compose up -d
```

## Files

| Path | Purpose |
|---|---|
| `docker-compose.yml` | tb-edge + tb-edge-postgres definition |
| `tb-edge-cloud.env.example` | template for the cloud connection env |
| `tb-edge-cloud.env` | real values — gitignored, lives on the edge |
