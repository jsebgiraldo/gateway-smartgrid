# 02 — Network

## Interfaces

| Interface | Type | Role | IPv4 | IPv6 | State |
|---|---|---|---|---|---|
| `lo` | loopback | — | 127.0.0.1/8 | ::1/128 | UP |
| `eth0` | physical | WAN (uplink) | 192.168.8.175/24 (DHCP) | `fdd8:3d8d:acf8::73d/128`, `fdd8:3d8d:acf8:0:2ecf:67ff:feff:a3dd/64` (SLAAC/DHCPv6) | UP |
| `eth1` | physical | bridged into `br-lan` | — | — | DOWN (no carrier) |
| `br-lan` | bridge | LAN gateway | 10.42.0.1/24 | `fdc3:5381:f776::1/60` | UP |
| `wlan0` | morse (HaLow) | radio0 AP, bridged to `br-lan` | — | link-local only | UP |
| `phy1-ap0` | mac80211 (5 GHz) | radio1 AP, bridged to `br-lan` | — | link-local only | UP |
| `morse0` | morse mgmt | Morse internal | — | — | DOWN |
| `wpan0` | 802.15.4 (OpenThread) | OTBR mesh radio | — | `fdde:ad00:beef:0:f820:9a70:166c:5f53/64` (mesh-local), `fdf1:a391:6243:2a67:f820:9a70:166c:5f53/64` | UP |
| `docker0` | bridge | Docker default | 172.17.0.1/16 | — | DOWN (no containers attached) |

> **`docker0` is DOWN** because the running containers (`tb-edge-v2`,
> `tb-edge-postgres`) use the host network or are connected via a different
> bridge — verify in [05_docker.md](05_docker.md).

## UCI network config

```
network.globals.ula_prefix='fdc3:5381:f776::/48'

# LAN
network.@device[0].name='br-lan'
network.@device[0].type='bridge'
network.@device[0].ports='eth1'
network.lan=interface
network.lan.device='br-lan'
network.lan.proto='static'
network.lan.ipaddr='10.42.0.1'
network.lan.netmask='255.255.255.0'
network.lan.ip6assign='60'

# WAN
network.wan.device='eth0'
network.wan.proto='dhcp'
network.wan6.device='eth0'
network.wan6.proto='dhcpv6'

# Docker (not auto, just keeps OpenWrt out of docker0's way)
network.docker.device='docker0'
network.docker.proto='none'
network.docker.auto='0'
network.@device[1].type='bridge'
network.@device[1].name='docker0'
```

## Routing

### IPv4

```
default via 192.168.8.1 dev eth0 proto static src 192.168.8.175
10.42.0.0/24 dev br-lan  proto kernel scope link src 10.42.0.1
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown
192.168.8.0/24 dev eth0   proto kernel scope link src 192.168.8.175
```

### IPv6

WAN has IPv6 connectivity via the upstream router (`fe80::9683:c4ff:fed0:d508`,
which is the GL-MT6000 router). Several prefixes are routed back through the
edge from the upstream:

- `fd67:4e18:3923::/64` and `fd90:996c:feb3:1::/64` — delegated from upstream
  router neighbours (other edge devices on the LAN?)
- `fdd8:3d8d:acf8::/64` — primary uplink IPv6 prefix
- `fdc3:5381:f776::/48` — local ULA, exported to br-lan as `fdc3:5381:f776::/64`
- `fdde:ad00:beef::/64` and `fdf1:a391:6243:2a67::/64` — Thread mesh-local on `wpan0`

## ARP / Neighbours

Active learned neighbours on `eth0` (LAN-side):

```
192.168.8.1   lladdr 94:83:c4:d0:d5:08 REACHABLE   # GL-MT6000 router
192.168.8.126 lladdr 04:99:b9:a1:e5:62 STALE       # another device on uplink LAN
```

## Firewall

Standard OpenWrt zones: `lan` (trusted, all ACCEPT) ↔ `wan` (REJECT in/forward,
ACCEPT out, masquerade). Stock `Allow-DHCP-Renew`, `Allow-Ping`, `Allow-IGMP`,
`Allow-DHCPv6`, `Allow-MLD`, `Allow-ICMPv6-Input/Forward`, `Allow-IPSec-ESP`,
`Allow-ISAKMP` rules.

`fw4` (nftables-based) is **not active** — the box is using legacy iptables/nft
hybrid. Docker has installed its full set of chains:
`DOCKER`, `DOCKER-USER`, `DOCKER-ISOLATION-STAGE-1/2`. The interesting
default-deny rule is:

```
DOCKER-USER: REJECT all from eth0 to docker0 with icmp-port-unreachable
```

→ traffic from the WAN cannot reach Docker bridge networks. If a future
container needs to be reachable from the LAN (e.g. ThingsBoard web UI), this
rule must be inspected before publishing ports.

`ip6tables` filter chains are empty (only INPUT/FORWARD/OUTPUT policy ACCEPT).
No IPv6 firewall protection beyond defaults — review before exposing IPv6
services.

## DHCP / dnsmasq

```
dhcp.@dnsmasq[0].domain='lan'
dhcp.@dnsmasq[0].local='/lan/'
dhcp.@dnsmasq[0].leasefile='/tmp/dhcp.leases'
dhcp.@dnsmasq[0].cachesize='1000'
dhcp.@dnsmasq[0].authoritative='1'

dhcp.lan.interface='lan'
dhcp.lan.start='100'
dhcp.lan.limit='150'
dhcp.lan.leasetime='12h'

dhcp.wan.ignore='1'   # never run DHCP server on WAN
```

LAN DHCP pool: `10.42.0.100 – 10.42.0.249`, 12 h lease. **`/tmp/dhcp.leases`
is empty** — no clients are currently connected to either radio (consistent
with the wifi_status snapshot in [03_wireless.md](03_wireless.md)).
