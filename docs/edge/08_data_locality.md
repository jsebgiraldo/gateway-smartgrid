# 08 — Data locality decision: postgres stays on the edge

**Status:** decided  ·  **Date:** 2026-05-16

## Context

The edge runs ThingsBoard Edge against a local `postgres:15-alpine`
container (`tb-edge-postgres`). The edge's RAM is tight (~ 250 MB
headroom — see [07_memory_budget.md](07_memory_budget.md)), and
moving postgres to the PC central (which has 30 GB free) would return
roughly **170 MB** to the edge — about 70 % more device headroom.

The question: should we do it?

## Decision

**No.** Postgres stays on the edge.

## Reasoning

ThingsBoard Edge exists to **operate during network outages to the
cloud / central server**. That is the only reason it is on the edge
device at all — otherwise the IoT devices could speak straight to the
central TB.

If postgres is moved to the central PC, every `tb-edge` DB call requires
the LAN path edge → PC. The moment the link is down (or the PC is
rebooting, or Docker Desktop restarts, or any of the many things we have
already seen happen on this PC):

- tb-edge cannot read or write its state
- LwM2M device sessions break or queue indefinitely
- The edge becomes worse than useless during the outage it was bought
  to handle

This wipes out the architectural property the edge was selected for.
The 170 MB of RAM is not worth that.

## What we do instead (alternative applied)

Tune postgres on the edge. The defaults (`shared_buffers=128MB`,
`effective_cache_size=4GB`, `max_connections=100`) assume a beefy
server; this edge has 1.85 GB total RAM and one app talking to the DB.

In `services/tb-edge/docker-compose.yml`, the `postgres` service gets
an explicit `command:` with:

| Setting | Default | Edge value | Reason |
|---|---|---|---|
| `shared_buffers` | 128 MB | **32 MB** | actual saving — postgres allocates this up-front |
| `effective_cache_size` | 4 GB | 128 MB | planner hint; tells PG it has limited filesystem cache |
| `maintenance_work_mem` | 64 MB | 16 MB | caps RAM spikes during VACUUM / index creation |
| `max_connections` | 100 | 20 | tb-edge uses ~ 10; each idle connection costs ~ 1 MB |
| `work_mem` | 4 MB | 4 MB (unchanged) | per-sort/hash; default is fine for IoT workload |

Expected saving: ~ 100 MB of `shared_buffers` + headroom from fewer
connection slots. Returned to the budget for new devices.

## When this decision might flip

- If the network between edge and PC becomes truly redundant
  (e.g., dual interface, automatic failover), AND
- The edge is genuinely never deployed in the field (only lab), AND
- We are RAM-starved enough that the trade is worth re-examining

Then revisit. Until then: postgres stays put.

## Related

- [07_memory_budget.md](07_memory_budget.md) — the budget that motivated this
- [services/tb-edge/docker-compose.yml](../../services/tb-edge/docker-compose.yml) — where the tuning lives
