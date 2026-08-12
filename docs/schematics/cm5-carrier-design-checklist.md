# CM5 Carrier Board — Design Checklist

Notas y checklist para la carrier propia compatible con CM5 (y otros SOMs) orientada a **edge gateway industrial / AMI**.
Documento de seguimiento — marcar `[x]` a medida que se incorpora al schematic / BoM.

- **Schematic actual:** [CM5_Project_20260508.pdf](CM5_Project_20260508.pdf)
- **Referencia comparada:** Seeed reComputer R1000 — <https://wiki.seeedstudio.com/recomputer_r/>
- **Fecha de creación:** 2026-05-28

---

## 1. Estado actual vs reComputer R1000

| Área | CM5_Project (actual) | reComputer R1000 |
|---|---|---|
| SoM | CM5 (PCIe Gen3, RP1) | CM4 (PCIe Gen2) |
| Mini PCIe | 2 slots (LTE + GP) | 1 |
| MikroBUS | 2 sockets | — |
| M.2 NVMe | Sí | Sí (Gen2) |
| USB-C | PD sink + RPiBoot dual-mode | — |
| Ethernet | 2x GbE | 1x GbE + 1x FE |
| HDMI / DSI | HDMI0 + HDMI1 + DSI | 1x HDMI 2.0 |
| Power in | PoE + DC jack + USB-C PD | 9-36 V DC + PoE |
| RS485 aislado | — | 3 canales |
| TPM 2.0 | — | SLB9670 opcional |
| Secure element | — | ATECC608A |
| RTC + batería | — | CR2032 backup |
| HW Watchdog externo | — | 1-255 s |
| Supercap UPS | — | LTC3350 opcional |
| Surge / ESD / EFT | no visible | EN61000 |
| Botones Reset/Reboot | — | Sí |

---

## 2. Requisitos del proyecto

- [x] 2 slots para LTE / NTN / WiMAX / Wi-Fi HaLow -> ya cubierto con 2x mini PCIe
- [x] Radios secundarios Wi-SUN / Thread / LoRa -> 2x mikroBUS + UART/SPI por GPIO expander
- [x] 2x Ethernet para LAN / SCADA -> ya cubierto
- [ ] RS485 / RS232 aislado para integracion industrial
- [ ] GPIO aislado tipo PLC (24 V)
- [ ] Compatibilidad con SOMs alternos (CM4 ya OK; evaluar SMARC en rev. 2)

---

## 3. ICs a incorporar — checklist por categoria

### A) Seguridad

- [ ] **TPM 2.0** — Infineon **OPTIGA SLB9672** (SPI, FIPS 140-3)
- [ ] **Secure Element** — NXP **SE050C2** (I2C, EdgeLock, AWS/Azure helpers, CC EAL6+)
      Alternativa low-cost: Microchip **ATECC608B**
- [ ] **Anti-tamper** (opcional AMI) — Maxim **DS28E38** (DeepCover)

### B) Time-keeping & Power Integrity

- [ ] **RTC con bateria** — NXP **PCF85063A** o Microchip **MCP7940N** (I2C)
      Alternativa robusta: Maxim **DS3231M** (MEMS, +-5 ppm)
- [ ] **Holdup CR2032** + portabateria
- [ ] **Supercap UPS** — Linear **LTC3350** (carga/balanceo 1-4 supercaps, PWR_FAIL)
      Alternativa: TI **BQ25171**
- [ ] **Voltage supervisor / watchdog externo** — TI **TPS3823** o Maxim **MAX6369**
- [ ] **Power-good aggregator** de las 5 rieles 3V3 — TI **TPS3702** discreto

### C) E/S industrial

- [ ] **RS485 aislado x2-x4** — Analog **ADM2587E** (5 kVrms, DC/DC integrado)
      Alternativa: TI **ISO1450**
- [ ] **RS232** — Maxim **MAX3232** o **SP3232E**
- [ ] **CAN aislado** (opcional EV/BMS) — TI **TCAN1462 + ISO1042**
- [ ] **GPIO aislado entrada 24V** (IEC 61131-2) — TI **ISO1212**
- [ ] **GPIO aislado salida** — TI **TPSI3052** o relevo estado solido **CPC1218**
- [ ] **Level shifter 1V8/3V3 <-> 5V** — TI **TXS0108E** o **NLSV2T244**

### D) Conectividad / radios

- [ ] Footprint **mikroBUS** para Wi-SUN FG25 (repo `firmware-ami-wisun-fg25`)
- [ ] Footprint para Thread/Matter — SiLabs **MGM240P** o Nordic **nRF54L15**
- [ ] **LoRa concentrador 8-canal** — Semtech **SX1303** via mPCIe (RAK2287/RAK5146)
- [ ] **Wi-Fi HaLow (802.11ah)** — Morse Micro **MM6108** o Newracom **NRC7292**
- [ ] **NTN / satelital** (opcional) — Sony **ALT1350** o u-blox **SARA-R510 NB10S**

### E) Red avanzada

- [ ] **Switch L2 administrado (TSN/AVB/MRP)** — Microchip **KSZ9897** (7 puertos GbE)
      Alternativa simple: Realtek **RTL8367N**
- [ ] **SPE 100BASE-T1** — TI **DP83TC811R-Q1** o NXP **TJA1101**

### F) Sensado de salud

- [ ] **Power monitor por riel** — TI **INA228** (20-bit) o **INA260**
- [ ] **Temperatura PCB** — TI **TMP117** (+-0.1 C) cerca de CM5 y radios
- [ ] **Acelerometro / tilt** — ST **LIS2DH12** (wake-on-motion, anti-tamper)
- [ ] **LED RGB driver** — NXP **PCA9956B** para panel frontal sin gastar GPIOs

### G) Proteccion

- [ ] **TVS Ethernet** — NXP **PESD2ETH** o magnetics con bypass (EN 61000-4-5)
- [ ] **TVS RS485** — TI **TPD2E007** o Bourns **CDSOT236** (8 kV ESD HBM)
- [ ] **TVS USB-C** — TI **TPD8S300**
- [ ] **Surge DC input** — Bourns **SMAJ** + fusible PTC
- [ ] Fusibles reseteables (PTC) en cada VBUS de salida

### H) Storage y misc

- [ ] **HAT ID EEPROM** — Microchip **AT24C256** (DT overlay automatico al CM5)
- [ ] **FRAM** para contadores AMI sin desgaste de eMMC — Fujitsu **MB85RC256V**
- [ ] **I2C mux** (si >8 dispositivos I2C) — TI **PCA9548A**

---

## 4. Compatibilidad multi-SOM

- [x] Footprint **DDR2-100 CM4/CM5** ya en uso -> abre catalogo: Radxa CM5, BPI-CM5, Pine64 SOQuartz
- [ ] Reservar area para **conector SMARC 2.1** (314-pin MXM-3) en rev. 2
- [ ] Adaptador CM5 <-> SMARC como PCB hijo (no rediseñar la carrier base)
- [ ] Documentar mapping de senales criticas (PCIe, USB3, GbE x2, MIPI, HDMI) en una tabla pinout

---

## 5. Prioridades por revision

### Rev. 1 (inmediata) — IMPRESCINDIBLES

- [ ] TPM 2.0 (SLB9672)
- [ ] Secure Element (SE050C2 o ATECC608B)
- [ ] RTC + supercap UPS (PCF85063A + LTC3350)
- [ ] Watchdog externo (TPS3823)
- [ ] RS485 aislado x2 (ADM2587E)
- [ ] TVS en USB-C, Ethernet, RS485, DC-in
- [ ] HAT ID EEPROM (AT24C256)
- [ ] Botones Reset / Reboot / User

### Rev. 2 — DESEABLES

- [ ] INA228 en VIN, 5V, 3V3_ALL_BOARD
- [ ] TMP117 (2 puntos) + LIS2DH12
- [ ] ISO1212 (4-8 entradas digitales 24 V)
- [ ] Switch KSZ9897 (anillo industrial)
- [ ] Footprint SMARC 2.1 reservado

### Rev. 3 — DIFERENCIADORES

- [ ] LoRa concentrador SX1303 (mPCIe)
- [ ] Footprint NTN (ALT1350)
- [ ] SPE 100BASE-T1
- [ ] Wi-Fi HaLow

---

## 6. Pendientes de decision

- [ ] Aislacion galvanica en RS485: 5 kV (industrial) vs 2.5 kV (basico)?
- [ ] Encapsulado / gabinete: IP40 (R1000) vs IP54+ (campo abierto AMI)?
- [ ] Rail DIN vs caja libre
- [ ] PoE: 802.3af (~13 W) suficiente o necesitamos at (~25 W) por LTE + LoRa + NVMe simultaneos?
- [ ] Wi-Fi/BLE: usar variante CM5 wireless o footprint M.2 1216 propio?
- [ ] Etiqueta de mercado: IEC 61131-2 (PLC), IEC 61850 (subestacion), o solo CE/FCC?
