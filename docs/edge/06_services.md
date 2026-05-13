# 06 — Services and packages

## init.d services (all enabled at boot)

All 51 services in `/etc/init.d/` are currently enabled — the image was not
trimmed for production. Grouped by purpose:

### Core OpenWrt
`boot`, `done`, `dropbear` (SSH), `firewall`, `log`, `network`, `rpcd`,
`sysctl`, `sysfixtime`, `sysntpd`, `system`, `ucitrack`, `uhttpd` (LuCI web
UI), `umdns`, `umount`, `urandom_seed`, `usbmode`, `wpad`, `cron`.

### Morse Micro / HaLow
`morse-boot-prints`, `morsechipreset`, `dppd` (DPP for HaLow onboarding),
`mesh11sd`, `prplmesh`, `trelay`.

### OpenThread Border Router
`otbr-agent`, `otbr-firewall`, `otbr-srp`, `otbr-addr-guard` — see
[04_otbr.md](04_otbr.md).

### Docker
`dockerd` — see [05_docker.md](05_docker.md).

### Media / IoT pipeline
| Service | Purpose | Notes |
|---|---|---|
| `mediamtx` | RTSP/RTMP/HLS streaming server | Suggests camera-stream relay use case |
| `camera-onvif-server` | ONVIF discovery server for IP cameras | Pairs with `mediamtx` |
| `aws_kvs` | AWS Kinesis Video Streams uploader | Cloud-side video sink |
| `pcm-manager` | Audio device manager | Possibly intercom / two-way audio |

### Auth / VPN / remote mgmt
`openvpn`, `radius`, `openwisp_config` (centralized OpenWRT fleet mgmt),
`ttyd` (web terminal — careful with exposure), `ser2net`, `socat`,
`gpio_switch`, `smart_manager`.

### Other
`avahi-daemon`, `dbus`, `dnsmasq`, `collectd`, `luci_statistics`, `led`,
`openssl`, `packet_steering`.

## Notable: services that should probably be disabled

For a smart-grid edge that is fundamentally a HaLow + Thread border gateway
plus ThingsBoard Edge container host, several services look out of place
and worth auditing:

- `aws_kvs`, `mediamtx`, `camera-onvif-server`, `pcm-manager` — only useful
  if this device is also acting as a video/audio relay. If not, drop them
  (saves boot time and rootfs).
- `prplmesh`, `mesh11sd`, `trelay` — multi-AP mesh stacks; only needed if
  more than one HaLow AP is in the deployment.
- `openvpn` — only if a VPN tunnel is part of the architecture.
- `radius` — only if HaLow / 5 GHz auth uses EAP, currently they use PSK.
- `openwisp_config` — useful for fleet management but exposes attack
  surface; confirm the controller URL and that TLS is enforced.
- `ttyd` — **web terminal**. Should be disabled or firewalled to LAN only.

## Packages of note (full count: 568)

Filtered list of project-relevant packages:

```
docker - 27.1.1-1
docker-compose - 2.18.1-1                # standalone binary, not the docker-cli plugin
dockerd - 27.1.1-1
kmod-morse - 5.15.167+1.16.4-3
luci-app-dockerman - v0.5.13-20240317    # LuCI web UI for Docker
luci-app-morseconfig
luci-app-morseguide
luci-app-morseupgrade
morse-bcf-info
morse-board-config / morse-board-config-hotplug-model
morse-bundle
morse-button / morse-leds / morse-mode
morse-copy-coredump
morse-dppd                               # DPP daemon for HaLow zero-touch provisioning
morse-firmware-sign
morse-fw-6108 (1.16.4-2)                 # WM6108 firmware (this board)
morse-fw-6108-tlm
morse-fw-8108 / -flm / -tlm              # WM8108 firmware (not this board, but bundled)
morse-regdb (v2.4.1-1)                   # regulatory database for HaLow
morse-wavemon                            # spectrum/signal monitor
morse_mesh11sd
morsecli (1.16.4-5)
netifd-morse
openthread-br - 1.0-1
python3-base / python3-light - 3.11.7
```

The duplicate fw packages (6108 + 8108 variants) inflate the image —
since this board is 6108-only, the 8108 firmware could be pruned in a
slimmer rebuild.

## Process snapshot at boot+9min

Top non-kernel processes (PID < 500):

- `procd` (PID 1) — service supervisor
- `ubusd` — system bus
- Active sessions (two `/sbin/askfirst /usr/libexec/login.sh` waiting on
  serial consoles)

Userspace daemons not in the kernel snapshot but expected based on enabled
services: `dropbear`, `uhttpd`, `dnsmasq`, `otbr-agent`, `dockerd`,
`mediamtx`, `wpa_supplicant`/`hostapd` for each radio, `mosquitto`
(if installed — not in the package grep). Capture a full `ps w` after
boot stabilization to confirm.
