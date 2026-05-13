# 01 — System

## Hardware

| Component | Value |
|---|---|
| Board | `seeed,r1000-wm6108` — Seeed reComputer R1000 with Morse Micro WM6108-SPI add-on |
| SoC | Broadcom BCM2711 (Raspberry Pi CM4 family), `bcm27xx/bcm2711` |
| CPU | 4× ARM Cortex-A72 (ARMv8, rev 3, `aarch64_cortex-a72`) |
| RAM | 1.85 GiB total (`MemTotal: 1 848 296 kB`) |
| Storage backing | squashfs rootfs + F2FS overlay (`f2fs_ckpt-7:0`, `f2fs_gc-7:0` kthreads present) |

## OS

```
DISTRIB_ID='OpenWrt'
DISTRIB_RELEASE='23.05.5'
DISTRIB_REVISION='r24310+1-b077cd4a1a'
DISTRIB_TARGET='bcm27xx/bcm2711'
DISTRIB_ARCH='aarch64_cortex-a72'
DISTRIB_DESCRIPTION='OpenWrt 23.05.5 Morse-2.9-dev'
DISTRIB_TAINTS='busybox'
```

Kernel: `Linux 5.15.167 #0 SMP Mon Feb 16 22:25:08 2026 aarch64`.

The `DISTRIB_REVISION` SHA suffix `b077cd4a1a` matches our pinned
[`repos/openwrt-morse @ b077cd4`](../../repos/openwrt-morse) submodule — meaning
this image was built from exactly the tree we have under orchestration.

## Resource snapshot (boot+9 min)

| Metric | Value | Notes |
|---|---|---|
| Uptime | 9 minutes | Recent reboot |
| Load avg | 1.00 / 1.61 / 1.07 | 1m≈1 with 4 cores → ~25 % busy |
| MemTotal | 1 848 MiB | |
| MemFree | 47 MiB | Linux page cache eats the rest |
| MemAvailable | 665 MiB | Effective free for new allocations |
| Buffers + Cached | 743 MiB | Healthy |
| Swap | none | |

## Storage — ⚠️ near full

| Mount | Total | Used | Free | % |
|---|---|---|---|---|
| `/` (rootfs+overlay) | 7.1 GiB | 6.7 GiB | **468 MiB** | **94 %** |
| `/tmp` (tmpfs) | 903 MiB | 1.3 MiB | 902 MiB | 0 % |

Filling drivers: ThingsBoard Edge postgres data lives in `/var/lib/docker/`
which is on the rootfs overlay. Without intervention, postgres growth or new
docker images will exhaust the filesystem.

Mitigation options (decide before next deploy):
1. Move `/var/lib/docker` to an external USB / NVMe mount.
2. Add a tmpfs backed `/var/lib/docker/tmp` for ephemeral data.
3. Aggressive postgres `VACUUM` schedule and ThingsBoard data retention policy.
4. Rebuild a slimmer rootfs (drop unused LuCI i18n, debug symbols).

## System UCI config

```
system.@system[0].hostname='r1000-wm6108-a3dd'
system.@system[0].timezone='<-05>5'
system.@system[0].zonename='America/Bogota'
system.@system[0].ttylogin='0'
system.@system[0].log_size='64'
system.@system[0].compat_version='1.0'
system.@system[0].default_wifi_key='<REDACTED>'   # see secrets/edge.env

system.ntp.enabled='1'
system.ntp.enable_server='0'
system.ntp.server='0.openwrt.pool.ntp.org' '1...' '2...' '3.openwrt.pool.ntp.org'
```

**Note**: `default_wifi_key` is the same string used as the WPA key on both
radios. Treat it as a secret — do not commit. See [03_wireless.md](03_wireless.md)
for the encryption configuration of each radio.
