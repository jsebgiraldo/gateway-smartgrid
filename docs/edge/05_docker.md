# 05 — Docker workloads

The edge runs Docker 27.1.1 internally with **two long-running containers**
that together form a ThingsBoard Edge instance (an IoT platform component
that synchronizes with a central ThingsBoard server).

## Running containers

| Name | Image | Image SHA | Size | Uptime |
|---|---|---|---|---|
| `tb-edge-v2` | `thingsboard/tb-edge:4.3.1.1EDGE` | `70fa0daa063c` | 1.16 GB | 9 min (since last boot) |
| `tb-edge-postgres` | `postgres:15-alpine` | `1032c552baa1` | 270 MB | 9 min |

Both containers have **no published ports** in `docker ps` and **no explicit
network** flag, so they're either on the default bridge (`docker0`, currently
DOWN with no IPs assigned) or on `--network host`. Given `docker0` is empty,
they're almost certainly running `--network host` — confirm with
`docker inspect tb-edge-v2 | grep -i network`.

That means ThingsBoard Edge is reachable on the edge device's host IPs
(192.168.8.175 from upstream, 10.42.0.1 from LAN clients) at whatever ports
the image binds (TB defaults: HTTP 8080, MQTT 1883, gRPC edge port 7070).

## Image inventory

```
REPOSITORY            TAG           IMAGE ID       CREATED       SIZE
postgres              15-alpine     1032c552baa1   3 weeks ago   270MB
thingsboard/tb-edge   4.3.1.1EDGE   70fa0daa063c   6 weeks ago   1.16GB
```

Total docker image footprint on the rootfs: **~1.43 GB**, which is most of
the reason `/` is at 94 %. Postgres data volumes (in `/var/lib/docker/`)
will keep growing.

## Networks

```
NETWORK ID     NAME      DRIVER    SCOPE
aef9efb7556a   bridge    bridge    local
ef23d82d4d9f   host      host      local
621c1b4a4c50   none      null      local
```

Only the three built-in Docker networks exist. No user-defined bridge — so
inter-container communication relies on host networking + localhost, not on
a private docker network.

## Open questions to answer next

1. **Is this ThingsBoard Edge connected to a central ThingsBoard server?**
   Check `tb-edge-v2` env for `CLOUD_RPC_HOST`, `CLOUD_RPC_PORT`,
   `CLOUD_ROUTING_KEY`, `CLOUD_ROUTING_SECRET`.
2. **Who deployed these containers and from what compose file?**
   `docker-compose` 2.18.1 is installed (`docker-compose` package, not the
   v2 plugin form). Look for `docker-compose.yml` under `/root`, `/etc`,
   `/opt`, or in the original deployment scripts.
3. **Postgres persistence path & size**: `docker inspect tb-edge-postgres
   --format '{{ .Mounts }}'` to find the volume location, then `du -sh`
   to size it. This is what will fill the rootfs.
4. **Backup strategy** for the postgres volume — currently none documented.
5. **Restart policy**: containers came back up after the recent reboot,
   so they have `--restart=unless-stopped` or `always`. Verify and version
   the compose file in this repo.

## Capturing the deployment manifest into version control

Once we identify the original `docker-compose.yml`, copy it into
`repos/` is not the right place (those are upstream submodules). Instead
create `services/tb-edge/` at orchestrator root with:

```
services/tb-edge/
  docker-compose.yml
  .env.example          # CLOUD_* variables, gitignored real .env
  README.md             # how to deploy / restart
```

This makes the deployment reproducible from the orchestrator alone.
