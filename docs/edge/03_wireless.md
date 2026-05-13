# 03 — Wireless

The edge ships two radios driven by different stacks. Both currently run as
APs bridged into `br-lan` (10.42.0.0/24), sharing the same SSID and key so
clients can roam transparently between sub-GHz HaLow and 5 GHz Wi-Fi.

| Radio | Driver | Band | Channel | Mode | Encryption | Iface | Stations |
|---|---|---|---|---|---|---|---|
| `radio0` | `morse` (MM6108) | S1G 11ah (sub-GHz HaLow) | 28 | AP + WDS | SAE (WPA3) | `wlan0` | 0 |
| `radio1` | `mac80211` | 5 GHz | 36 (VHT80) | AP | psk2 (WPA2) | `phy1-ap0` | 0 |

Both broadcast SSID **`r1000-wm6108-a3dd`** with the **same pre-shared key**
(value lives in `system.@system[0].default_wifi_key` — see
[01_system.md](01_system.md), do not commit).

## radio0 — Morse Micro HaLow (802.11ah)

```
wireless.radio0.type='morse'
wireless.radio0.path='platform/soc/fe204000.spi/spi_master/spi0/spi0.1'
wireless.radio0.band='s1g'
wireless.radio0.hwmode='11ah'
wireless.radio0.bcf='bcf_fgh100mhaamd.bin'
wireless.radio0.channel='28'
wireless.radio0.htmode='NOHT'
wireless.radio0.country='US'         # ⚠️ verify regulatory domain matches deployment country
wireless.radio0.reconf='0'

wireless.default_radio0.mode='ap'
wireless.default_radio0.wds='1'      # 4-address mode for L2 bridging
wireless.default_radio0.device='radio0'
wireless.default_radio0.network='lan'
wireless.default_radio0.ssid='r1000-wm6108-a3dd'
wireless.default_radio0.encryption='sae'
```

Interesting facts:

- BCF (board config file) is `bcf_fgh100mhaamd.bin` → MM6108 antenna model.
- WDS mode enabled (4-address frames), required to bridge HaLow clients into
  `br-lan` transparently.
- **Country code `US`** — channel plan and TX power follow FCC HaLow rules.
  If deploying in Colombia (where the test bench is, per system zonename),
  recheck the local regulatory mapping — Colombia is typically `CO` and may
  use a different channel set. Misconfiguration here is a compliance risk.
- `morsectrl` is **not installed** on this image (`which morsectrl` → not
  found), so out-of-band tuning/diagnostics happen via `iw`, `ubus`, or the
  LuCI MorseConfig app (`luci-app-morseconfig` is installed).
- `morse0` interface exists but is DOWN — Morse management / mon interface,
  surfaces only when actively used.

## radio1 — 5 GHz Wi-Fi (mac80211)

```
wireless.radio1.type='mac80211'
wireless.radio1.path='platform/soc/fe300000.mmcnr/mmc_host/mmc1/mmc1:0001/mmc1:0001:1'
wireless.radio1.channel='36'
wireless.radio1.band='5g'
wireless.radio1.htmode='VHT80'

wireless.default_radio1.device='radio1'
wireless.default_radio1.network='lan'
wireless.default_radio1.mode='ap'
wireless.default_radio1.ssid='r1000-wm6108-a3dd'
wireless.default_radio1.encryption='psk2'
```

`iw dev` output confirms:

```
Interface phy1-ap0
  ssid r1000-wm6108-a3dd
  type AP
  channel 36 (5180 MHz), width: 80 MHz, center1: 5210 MHz
  txpower 31.00 dBm
```

`iw dev` also reports a separate `wlan0` running on channel 112 (5560 MHz,
160 MHz), which is the HaLow chip being exposed through mac80211 for
compatibility — the actual HaLow operation happens on sub-GHz via the
`morse` driver. Treat the `iw` reading for `wlan0` as informational, not
authoritative.

## Live status (no associated clients)

`ubus call network.wireless status` returns both radios as `up: true,
pending: false, autostart: true, disabled: false` with empty `stations: []`
on each interface — the radios are alive but nobody is connected.

## To-dos before production

- [ ] Confirm regulatory country code for deployment site (likely `CO`, not
      `US`); rebuild HaLow channel plan accordingly.
- [ ] Decide whether HaLow and 5 GHz should keep the same SSID (current) or
      split for traffic shaping / observability.
- [ ] Rotate `default_wifi_key` from the per-board default to a deployment
      secret stored in `secrets/edge.env` and applied via UCI script.
- [ ] Add station counters / RSSI to operational dashboard once at least one
      HaLow client is provisioned.
