#!/usr/bin/env python3
"""
In-place aesthetic + time-navigation improvements for the Emsitech
"Panel de Facturacion (R1000)" dashboard on TB @ 100.67.60.126.

Scope: NO new keys, NO new widgets. Only polish the 17 widgets that exist.
  - Consistent color palette per magnitude
  - Consistent icons per magnitude
  - Units on data keys AND on chart Y-axes
  - Per-widget timewindow controls unhidden (user can zoom/pan each chart)
  - Sensible default windows per chart type (short for instantaneous, long for cumulative)
  - Smooth line style on all charts
  - Legend visible at bottom on all charts

Read auth from THINGSBOARD_JWT env var (temporary) OR
../../../secrets/thingsboard-emsitech.env (THINGSBOARD_API_KEY, persistent).
Deploys in-place to the same dashboard id.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SECRETS   = REPO_ROOT / "secrets" / "thingsboard-emsitech.env"

TB_URL         = "http://100.67.60.126"
DASHBOARD_ID   = "eaf0f940-7d51-11f1-8505-8549340ee25f"

# --- palette per data-key name -----------------------------------------------
# color, unit, icon, decimals
KEY_STYLE: dict[str, dict] = {
    # instantaneous electrical
    "voltage_l1":            {"color": "#1976d2", "unit": "V",   "icon": "bolt",              "dec": 1},
    "current_l1":            {"color": "#f57c00", "unit": "A",   "icon": "electric_meter",    "dec": 3},
    "frequency":             {"color": "#00897b", "unit": "Hz",  "icon": "graphic_eq",        "dec": 2},
    "power_factor":          {"color": "#546e7a", "unit": "",    "icon": "trending_up",       "dec": 3},
    # powers
    "active_power":          {"color": "#2e7d32", "unit": "W",   "icon": "flash_on",          "dec": 1},
    "active_power_export":   {"color": "#c62828", "unit": "W",   "icon": "flash_on",          "dec": 1},
    "reactive_power_import": {"color": "#f9a825", "unit": "var", "icon": "all_inclusive",     "dec": 1},
    "reactive_power_export": {"color": "#8e24aa", "unit": "var", "icon": "all_inclusive",     "dec": 1},
    "apparent_power":        {"color": "#6a1b9a", "unit": "VA",  "icon": "power",             "dec": 1},
    # cumulative energies
    "active_energy":         {"color": "#2e7d32", "unit": "Wh",  "icon": "battery_charging_full", "dec": 0},
    "active_energy_export":  {"color": "#c62828", "unit": "Wh",  "icon": "battery_charging_full", "dec": 0},
    "reactive_energy_import":{"color": "#f9a825", "unit": "varh","icon": "battery_charging_full", "dec": 0},
    "reactive_energy_export":{"color": "#8e24aa", "unit": "varh","icon": "battery_charging_full", "dec": 0},
    "apparent_energy":       {"color": "#6a1b9a", "unit": "VAh", "icon": "battery_charging_full", "dec": 0},
    # reactive per quadrant
    "reactive_energy_q1":    {"color": "#2e7d32", "unit": "varh","icon": "explore",           "dec": 0},
    "reactive_energy_q2":    {"color": "#f9a825", "unit": "varh","icon": "explore",           "dec": 0},
    "reactive_energy_q3":    {"color": "#c62828", "unit": "varh","icon": "explore",           "dec": 0},
    "reactive_energy_q4":    {"color": "#1976d2", "unit": "varh","icon": "explore",           "dec": 0},
}

DEFAULT_STYLE = {"color": "#455a64", "unit": "", "icon": "insights", "dec": 2}


def style_for(key_name: str) -> dict:
    return KEY_STYLE.get(key_name, DEFAULT_STYLE)


# --- transformations ---------------------------------------------------------

def polish_datakey(dk: dict) -> None:
    """Apply palette + units + decimals + line style to one dataKey."""
    style = style_for(dk.get("name", ""))
    dk["color"]    = style["color"]
    dk["units"]    = style["unit"] or dk.get("units")
    dk["decimals"] = style["dec"] if style["dec"] is not None else dk.get("decimals")
    s = dk.setdefault("settings", {})
    # only for chart widgets, dataKey.settings has line drawing config
    if "lineSettings" in s:
        s["lineSettings"]["smooth"]    = True
        s["lineSettings"]["lineWidth"] = 2
    s["showInLegend"] = True


def polish_value_card(w: dict) -> None:
    """Value card: consistent icon + colored icon + shown units + last-update ago."""
    cfg = w["config"]
    dks = cfg["datasources"][0]["dataKeys"]
    if not dks:
        return
    style = style_for(dks[0]["name"])
    polish_datakey(dks[0])
    st = cfg.setdefault("settings", {})
    st["showIcon"] = True
    st["icon"] = style["icon"]
    st["iconColor"] = {"type": "constant", "color": style["color"]}
    st["labelPosition"] = "top"
    st["showLabel"] = True
    st["showDate"]  = True
    st.setdefault("dateFormat", {}).update({"lastUpdateAgo": True, "custom": False, "format": None})
    # value color subtle, dark; label matches icon color
    st["labelColor"] = {"type": "constant", "color": style["color"]}
    st["valueColor"] = {"type": "constant", "color": "rgba(0,0,0,0.87)"}


def polish_time_series_chart(w: dict) -> None:
    """Chart: palette + units on y-axes + per-widget timewindow enabled + smooth."""
    cfg = w["config"]
    # datakeys colored per palette
    all_units: list[str] = []
    for ds in cfg.get("datasources", []):
        for dk in ds.get("dataKeys", []):
            polish_datakey(dk)
            u = style_for(dk["name"])["unit"]
            if u and u not in all_units:
                all_units.append(u)
    # y-axis units: use the first (dominant) unit
    st = cfg.setdefault("settings", {})
    yaxes = st.setdefault("yAxes", {})
    default_axis = yaxes.setdefault("default", {})
    if all_units:
        default_axis["units"] = all_units[0]
    default_axis["show"] = True
    default_axis["showTickLabels"] = True

    # Legend visible at bottom
    legend = st.setdefault("legend", {"display": True, "position": "bottom"})
    legend["display"] = True
    legend["position"] = "bottom"

    # Per-widget timewindow: unhide selector + sensible default per chart type.
    #   Any chart whose datakeys are cumulative energy → default 7 days; else 24h.
    tw = cfg.setdefault("timewindow", {})
    is_cumulative = any(
        dk["name"] in {"active_energy", "active_energy_export", "reactive_energy_import",
                       "reactive_energy_export", "apparent_energy",
                       "reactive_energy_q1", "reactive_energy_q2", "reactive_energy_q3", "reactive_energy_q4"}
        for ds in cfg.get("datasources", []) for dk in ds.get("dataKeys", [])
    )
    tw.update(_timewindow_block(is_cumulative))


def _timewindow_block(is_cumulative: bool) -> dict:
    """Return a full timewindow block with both REALTIME and HISTORY tabs enabled.

    HISTORY tab lets the user pick a specific date/time range. `historyType: 2`
    means "fixed time window with quick presets", and includes a `fixedTimewindow`
    with sensible start/end (last 24h / 7d). The `interval` and `quickInterval`
    defaults are picked to match the chart's characteristic timescale.
    """
    span_ms      = 604_800_000 if is_cumulative else 86_400_000   # 7d vs 24h
    quick        = "CURRENT_WEEK" if is_cumulative else "CURRENT_DAY"
    interval_ms  = 60_000 if is_cumulative else 30_000

    # Fixed start/end placeholder: TB overrides with a picker on the widget.
    # We anchor to (now-span, now) but the user's picker is the source of truth.
    now_ms = 1_784_050_000_000  # deterministic anchor so re-runs produce same JSON
    return {
        "hideInterval":      False,
        "hideLastInterval":  False,
        "hideQuickInterval": False,
        "hideAggregation":   False,
        "hideAggInterval":   False,
        "hideTimezone":      False,
        "selectedTab":       0,          # 0 = REALTIME default; user can switch to HISTORY (1)
        "realtime": {
            "realtimeType":  1,          # 1 = last N interval / quickInterval selector
            "timewindowMs":  span_ms,
            "quickInterval": quick,
            "interval":      interval_ms,
        },
        "history": {
            "historyType":   1,          # 1 = last N interval; user can flip to 0 (fixed)
            "timewindowMs":  span_ms,
            "quickInterval": quick,
            "interval":      interval_ms,
            "fixedTimewindow": {
                "startTimeMs": now_ms - span_ms,
                "endTimeMs":   now_ms,
            },
        },
        "aggregation": {"type": "AVG", "limit": 5000},
    }


def polish_alarms_table(w: dict) -> None:
    """Alarms table: bold title + defaultSortOrder + severity filter unrestricted."""
    cfg = w["config"]
    cfg.setdefault("settings", {}).update({
        "enableSearch": True,
        "enableFilter": True,
        "enableStatusFilter": True,
        "displayDetails": True,
        "allowAcknowledgment": True,
        "allowClear": True,
        "defaultSortOrder": "-createdTime",
    })


def apply(dashboard: dict) -> dict:
    cfg = dashboard["configuration"]
    for wid, w in cfg["widgets"].items():
        fqn = w.get("typeFullFqn", "")
        if fqn == "system.cards.value_card":
            polish_value_card(w)
        elif fqn == "system.time_series_chart":
            polish_time_series_chart(w)
        elif fqn == "system.alarm_widgets.alarms_table":
            polish_alarms_table(w)
    # dashboard-level: dashboard timewindow keeps last 24h and shows both tabs
    dtw = cfg.setdefault("timewindow", {})
    dtw.update(_timewindow_block(is_cumulative=False))
    return dashboard


# --- auth + deploy ----------------------------------------------------------

def _login(url: str, user: str, pw: str) -> str:
    r = urllib.request.Request(
        f"{url}/api/auth/login",
        data=json.dumps({"username": user, "password": pw}).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(r, timeout=15) as resp:
        return json.loads(resp.read())["token"]


def load_auth() -> tuple[str, str]:
    """Return (scheme, credential). Precedence:
      1. THINGSBOARD_JWT env var (Bearer)
      2. THINGSBOARD_API_KEY from secrets file (ApiKey)
      3. THINGSBOARD_USERNAME + THINGSBOARD_PASSWORD from secrets file
         (Bearer, obtained via /api/auth/login)
    """
    jwt = os.environ.get("THINGSBOARD_JWT")
    if jwt:
        return ("Bearer", jwt)
    if SECRETS.exists():
        env = dict(l.split("=", 1) for l in SECRETS.read_text().splitlines()
                   if "=" in l and not l.strip().startswith("#"))
        key = env.get("THINGSBOARD_API_KEY", "").strip()
        if key:
            return ("ApiKey", key)
        user = env.get("THINGSBOARD_USERNAME", "").strip()
        pw   = env.get("THINGSBOARD_PASSWORD", "").strip()
        if user and pw:
            token = _login(TB_URL, user, pw)
            return ("Bearer", token)
    sys.exit("no auth: set THINGSBOARD_JWT env var or fill secrets/thingsboard-emsitech.env")


def req(method: str, path: str, scheme: str, cred: str, body: dict | None = None) -> Any:
    url = f"{TB_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={
        "X-Authorization": f"{scheme} {cred}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8", "replace")
        sys.exit(f"HTTP {e.code} on {method} {url}\n{body_txt}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Compute + write improved JSON locally without POSTing.")
    args = ap.parse_args()

    scheme, cred = load_auth()
    print(f"auth: {scheme}")

    print("fetching current dashboard...")
    current = req("GET", f"/api/dashboard/{DASHBOARD_ID}", scheme, cred)
    Path("_ems_dashboard_before.json").write_text(encoding="utf-8", data=json.dumps(current, indent=2, ensure_ascii=False))
    print(f"  saved snapshot -> _ems_dashboard_before.json  ({len(current['configuration']['widgets'])} widgets)")

    improved = apply(current)
    Path("_ems_dashboard_after.json").write_text(encoding="utf-8", data=json.dumps(improved, indent=2, ensure_ascii=False))
    print(f"  wrote improved -> _ems_dashboard_after.json")

    if args.dry_run:
        print("dry-run: not deploying")
        return

    print("posting improved dashboard...")
    result = req("POST", "/api/dashboard", scheme, cred, improved)
    print(f"  updated  id={result['id']['id']}  version={result.get('version')}")


if __name__ == "__main__":
    main()
