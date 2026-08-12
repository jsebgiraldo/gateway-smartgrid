#!/usr/bin/env python3
"""
Builds the AMI LwM2M Monitoring dashboard JSON for ThingsBoard 4.3.

v3: mirrors the EXACT entityAliases + settings from the working
"AMI Fleet Health" dashboard. Only the title and extra columns change.
Plain-ASCII title (no mojibake from Unicode dashes).

Output: ami-lwm2m-monitoring.json (POSTed by deploy.py).
Re-run is safe — emits a deterministic JSON.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

# Deterministic ids — match the reference dashboard's alias UUID exactly so
# the entityAliasId reference is identical.
def _id(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ami-monitoring/v3/{name}"))

ALIAS_AMI       = "f2bb1bd0-4c61-4d90-9653-410fca842678"
ALIAS_ALL_DEVS  = "37be124c-8806-474f-8657-de676c5bb73c"

WID_ALARMS  = _id("widget/alarms-table")
WID_DEVICES = _id("widget/devices-table")


def col(name: str, type_: str, label: str | None = None) -> dict:
    return {
        "name": name,
        "label": label or name,
        "type": type_,
        "columnWidth": "0px",
        "useCellStyleFunction": False,
        "useCellContentFunction": False,
    }


def widget_alarms_table() -> dict:
    # Byte-for-byte clone of the working baseline.
    return {
        "typeFullFqn": "system.alarm_widgets.alarms_table",
        "type": "alarm",
        "sizeX": 24, "sizeY": 8, "row": 0, "col": 0,
        "config": {
            "title": "Active fleet alarms",
            "showTitle": True,
            "datasources": [
                {"type": "alarmCount", "name": "Fleet alarms"},
            ],
            "alarmSource": {"type": "function", "name": "Alarms"},
            "alarmFilterConfig": {
                "statusList": ["ACTIVE"],
                "severityList": [],
                "typeList": [],
                "searchPropagatedAlarms": True,
            },
            "settings": {
                "enableSelection": False,
                "enableSearch": True,
                "displayDetails": True,
                "enableFilter": True,
                "defaultSortOrder": "-createdTime",
            },
        },
    }


def widget_devices_table() -> dict:
    return {
        "typeFullFqn": "system.entity_widgets.entities_table",
        "type": "latest",
        "sizeX": 24, "sizeY": 16, "row": 8, "col": 0,
        "config": {
            "title": "AMI fleet nodes - health, electrical, LwM2M, MAC",
            "showTitle": True,
            "datasources": [
                {
                    "type": "entity",
                    "name": "AMI nodes",
                    "entityAliasId": ALIAS_AMI,
                    "dataKeys": [
                        # ----- baseline that the working dashboard has (verified rendering) -----
                        col("active",          "attribute",  "Active"),
                        col("thread_role",     "timeseries", "Thread role"),
                        col("uptime_s",        "timeseries", "Uptime (s)"),
                        col("reg_success",     "timeseries", "Reg OK"),
                        col("recover_count",   "timeseries", "Recoveries"),
                        col("watchdog_count",  "timeseries", "Watchdog"),
                        col("last_error_code", "timeseries", "Last err"),
                        col("voltage",         "timeseries", "V"),
                        col("frequency",       "timeseries", "Hz"),
                        # ----- safe additions (all keys verified via /api/plugins/telemetry/...) -----
                        col("fw_version",      "attribute",  "FW"),
                        col("total_resets",    "timeseries", "Resets"),
                        col("current",         "timeseries", "A"),
                        col("activePower",     "timeseries", "P (W)"),
                        col("reactivePower",   "timeseries", "Q (var)"),
                        col("apparentPower",   "timeseries", "S (VA)"),
                        col("powerFactor",     "timeseries", "PF"),
                        col("activeEnergy",    "timeseries", "E act (Wh)"),
                        col("temperature",     "timeseries", "T (C)"),
                        col("reg_attempts",    "timeseries", "Reg try"),
                        col("notify_emitted",  "timeseries", "Notify"),
                        col("notify_throttled","timeseries", "Notify thr"),
                        col("mac_tx_total",    "timeseries", "MAC TX"),
                        col("mac_rx_total",    "timeseries", "MAC RX"),
                        col("mac_tx_err_abort","timeseries", "TX err"),
                        col("mac_rx_err_no_frame", "timeseries", "RX err"),
                    ],
                },
            ],
            "settings": {
                "entitiesTitle": "AMI fleet nodes",
                "enableSearch": True,
                "displayEntityName": True,
                "displayEntityLabel": False,   # matches ref — true caused widget error
                "displayEntityType": False,
                "defaultSortOrder": "entityName",
            },
        },
    }


def assemble() -> dict:
    widgets = {
        WID_ALARMS:  widget_alarms_table(),
        WID_DEVICES: widget_devices_table(),
    }
    layout_widgets = {
        WID_ALARMS:  {"sizeX": 24, "sizeY": 8,  "row": 0, "col": 0},
        WID_DEVICES: {"sizeX": 24, "sizeY": 16, "row": 8, "col": 0},
    }
    return {
        "title": "AMI LwM2M - Monitoring",
        "image": None,
        "mobileHide": False,
        "configuration": {
            "description": (
                "AMI ESP32-C6 LwM2M nodes over Thread 802.15.4. "
                "Active alarms + per-node table covering health, electrical (COSEM), "
                "LwM2M registration, and 802.15.4 MAC counters."
            ),
            "widgets": widgets,
            "states": {
                "default": {
                    "name": "AMI LwM2M - Monitoring",
                    "root": True,
                    "layouts": {
                        "main": {
                            "widgets": layout_widgets,
                            "gridSettings": {
                                "backgroundColor": "#eeeeee",
                                "columns": 24,
                                "margin": 10,
                                "outerMargin": True,
                            },
                        },
                    },
                },
            },
            # Exact clone of the working dashboard's aliases (same UUIDs, same fields).
            "entityAliases": {
                ALIAS_AMI: {
                    "id": ALIAS_AMI,
                    "alias": "AMI nodes",
                    "filter": {
                        "type": "deviceType",
                        "resolveMultiple": True,
                        "deviceType": "AMI_LwM2M_Node",
                        "deviceNamePattern": "ami-esp32c6",
                    },
                },
                ALIAS_ALL_DEVS: {
                    "id": ALIAS_ALL_DEVS,
                    "alias": "All devices",
                    "filter": {
                        "type": "deviceType",
                        "resolveMultiple": True,
                        "deviceType": "AMI_LwM2M_Node",
                    },
                },
            },
            "timewindow": {"realtime": {"timewindowMs": 3600000}},
            "settings": {
                "stateControllerId": "entity",
                "showTitle": True,
                "showDashboardsSelect": True,
            },
        },
    }


def main() -> None:
    out = Path(__file__).parent / "ami-lwm2m-monitoring.json"
    out.write_text(json.dumps(assemble(), indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
