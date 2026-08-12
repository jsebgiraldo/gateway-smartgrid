#!/usr/bin/env python3
"""
Idempotent deploy of TB dashboard JSONs to the central server and assignment to edges.

Usage:
  python deploy.py ami-lwm2m-monitoring.json                # create or update on central
  python deploy.py ami-lwm2m-monitoring.json --edge edge-pi4-ekh01

Reads API key from ../../../secrets/thingsboard-local.env (THINGSBOARD_API_KEY + THINGSBOARD_URL).
On Docker Desktop the env file uses http://host.docker.internal:8080 — when running this script
directly from the host, we rewrite that to http://localhost:8080.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SECRETS   = REPO_ROOT / "secrets" / "thingsboard-local.env"


def load_env() -> tuple[str, str]:
    if not SECRETS.exists():
        sys.exit(f"missing {SECRETS}")
    env = {}
    for line in SECRETS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k] = v
    url = env.get("THINGSBOARD_URL", "").replace("host.docker.internal", "localhost")
    key = env.get("THINGSBOARD_API_KEY", "")
    if not (url and key):
        sys.exit("THINGSBOARD_URL or THINGSBOARD_API_KEY missing")
    return url, key


def req(method: str, url: str, key: str, body: dict | None = None) -> dict | list | None:
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={
        "X-Authorization": f"ApiKey {key}",
        "Content-Type": "application/json",
        "Accept":       "application/json",
    })
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit(f"HTTP {e.code} on {method} {url}\n{body}")


def find_dashboard(base: str, key: str, title: str) -> dict | None:
    page = 0
    while True:
        data = req("GET", f"{base}/api/tenant/dashboards?pageSize=100&page={page}", key)
        for d in data["data"]:
            if d["title"] == title:
                return d
        if not data.get("hasNext"):
            return None
        page += 1


def find_edge(base: str, key: str, name: str) -> dict | None:
    page = 0
    while True:
        data = req("GET", f"{base}/api/edges?pageSize=100&page={page}", key)
        for e in data["data"]:
            if e["name"] == name:
                return e
        if not data.get("hasNext"):
            return None
        page += 1


def upsert(base: str, key: str, dashboard: dict) -> dict:
    existing = find_dashboard(base, key, dashboard["title"])
    if existing:
        dashboard["id"] = existing["id"]
        # POST /api/dashboard updates when id is present
        result = req("POST", f"{base}/api/dashboard", key, dashboard)
        print(f"updated dashboard '{dashboard['title']}'  id={result['id']['id']}")
    else:
        result = req("POST", f"{base}/api/dashboard", key, dashboard)
        print(f"created dashboard '{dashboard['title']}'  id={result['id']['id']}")
    return result


def assign_to_edge(base: str, key: str, dashboard_id: str, edge_name: str) -> None:
    edge = find_edge(base, key, edge_name)
    if not edge:
        sys.exit(f"edge '{edge_name}' not found")
    edge_id = edge["id"]["id"]
    # already assigned?
    page = 0
    assigned = False
    while True:
        d = req("GET", f"{base}/api/edge/{edge_id}/dashboards?pageSize=100&page={page}", key)
        if any(x["id"]["id"] == dashboard_id for x in d["data"]):
            assigned = True
            break
        if not d.get("hasNext"):
            break
        page += 1
    if assigned:
        print(f"already assigned to edge '{edge_name}' ({edge_id})")
        return
    req("POST", f"{base}/api/edge/{edge_id}/dashboard/{dashboard_id}", key)
    print(f"assigned to edge '{edge_name}' ({edge_id})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dashboard_json", help="Path to dashboard JSON file")
    ap.add_argument("--edge", help="Edge name to assign the dashboard to", default=None)
    args = ap.parse_args()

    url, key = load_env()
    path = Path(args.dashboard_json)
    if not path.is_absolute():
        path = Path(__file__).parent / path
    dash = json.loads(path.read_text())

    result = upsert(url, key, dash)
    if args.edge:
        assign_to_edge(url, key, result["id"]["id"], args.edge)


if __name__ == "__main__":
    main()
