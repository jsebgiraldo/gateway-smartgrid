"""Assemble the new page 2 (CM5 Pinout) XML and emit ready-to-paste content."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

with open("pinout_cells.xml", encoding="utf-8") as f:
    grid_cells = f.read()

# Split J1 and J2 sections (gen_cm5_pinout emits J1 first, blank line, then J2)
# Container cell must appear BEFORE its child cells in XML order, otherwise
# drawio renders the container on top and hides the cells inside.
parts = grid_cells.split("\n\n", 1)
j1_cells = parts[0]
j2_cells = parts[1] if len(parts) > 1 else ""

HEADER = '''  <diagram name="CM5 Pinout" id="cm5-pinout">
    <mxGraphModel dx="3000" dy="2200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1980" pageHeight="1300" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <mxCell id="2" parent="1" vertex="1" value="&lt;b&gt;CM5 Pinout — Grilla visual de pines&lt;/b&gt;&lt;br&gt;200 pines (2× Hirose DF40 · 0.4 mm pitch) · Color = clase de señal · Borde sólido = ASIGNADO en CM5_Project · Borde punteado = LIBRE / disponible" style="text;html=1;align=center;verticalAlign=middle;fontSize=14;fontFamily=Helvetica;">
          <mxGeometry x="240" y="30" width="1500" height="60" as="geometry" />
        </mxCell>

        <mxCell id="10" parent="1" vertex="1" value="&lt;b&gt;J1 — Connector 1 (South) · Pins 1–100&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=3;fontSize=13;verticalAlign=top;spacingTop=10;">
          <mxGeometry x="60" y="110" width="540" height="940" as="geometry" />
        </mxCell>

'''

J2_CONTAINER = '''
        <mxCell id="20" parent="1" vertex="1" value="&lt;b&gt;J2 — Connector 2 (North) · Pins 101–200&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=3;fontSize=13;verticalAlign=top;spacingTop=10;">
          <mxGeometry x="1260" y="110" width="540" height="940" as="geometry" />
        </mxCell>

'''

MIDDLE_NOTES = '''
        <mxCell id="40" parent="1" vertex="1" value="&lt;b&gt;Resumen por estado&lt;/b&gt;" style="text;html=1;align=center;fontSize=13;fontColor=#333333;">
          <mxGeometry x="630" y="110" width="600" height="25" as="geometry" />
        </mxCell>

        <mxCell id="41" parent="1" vertex="1" value="&lt;font style=&quot;font-size:11px&quot;&gt;&lt;b&gt;✅ ASIGNADOS (borde sólido):&lt;/b&gt;&lt;br&gt;• Ethernet RGMII (J1 1-22)&lt;br&gt;• USB 2.0 (J2 101-105)&lt;br&gt;• PCIe Gen3 x1 (J2 102-129)&lt;br&gt;• HDMI0 (J2 135-163)&lt;br&gt;• HAT EEPROM I²C0 (J2 122, 124)&lt;br&gt;• nRPI_BOOT + GLOBAL_EN + RUN_PG + nEXTRST&lt;br&gt;• GPIO 0-5, 7-11, 14-27 (UART/I²C/SPI/control)&lt;br&gt;• +5V x6 (J2 177-187) + VBAT (190) + Fan_PWM (197)&lt;br&gt;• +3V3 + todos los GND&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6ffe6;strokeColor=#228B22;strokeWidth=2;fontSize=10;align=left;spacingLeft=12;verticalAlign=top;spacingTop=8;">
          <mxGeometry x="630" y="140" width="600" height="220" as="geometry" />
        </mxCell>

        <mxCell id="42" parent="1" vertex="1" value="&lt;font style=&quot;font-size:11px&quot;&gt;&lt;b&gt;🆓 LIBRES (borde punteado):&lt;/b&gt;&lt;br&gt;• CAM1 MIPI CSI (J1 24-50) — cámara&lt;br&gt;• DSI1 MIPI (J1 54-78) — display secundario&lt;br&gt;• DSI0 MIPI (J1 84-98) — display 7&quot; touch&lt;br&gt;• HDMI1 (J2 132-162) — segundo display&lt;br&gt;• SD card alterno (J2 167-174) — solo si no usás eMMC&lt;br&gt;• GPIO 6, 12, 13 — uso futuro&lt;br&gt;• Pines deprecated (J2 182, 184, 186, 188)&lt;br&gt;• nUSB_BOOT (J2 112), CAM_GPIO (127), VDAC_COMP (128)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=#CC0000;strokeWidth=1;strokeDasharray=3 3;fontSize=10;align=left;spacingLeft=12;verticalAlign=top;spacingTop=8;">
          <mxGeometry x="630" y="375" width="600" height="200" as="geometry" />
        </mxCell>

        <mxCell id="43" parent="1" vertex="1" value="&lt;b&gt;Leyenda — Color por clase de señal&lt;/b&gt;" style="text;html=1;align=center;fontSize=12;">
          <mxGeometry x="630" y="595" width="600" height="22" as="geometry" />
        </mxCell>

        <mxCell id="44" parent="1" vertex="1" value="High-speed differential pair (PCIe / USB / HDMI / Ethernet / MIPI)" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;strokeWidth=2;fontSize=10;">
          <mxGeometry x="630" y="625" width="600" height="22" as="geometry" />
        </mxCell>
        <mxCell id="45" parent="1" vertex="1" value="GPIO / single-ended signal (incl. SDIO, mikroBUS signals)" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;strokeWidth=2;fontSize=10;">
          <mxGeometry x="630" y="652" width="600" height="22" as="geometry" />
        </mxCell>
        <mxCell id="46" parent="1" vertex="1" value="Power rails (+3V3, +5V, VBAT)" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2;fontSize=10;">
          <mxGeometry x="630" y="679" width="600" height="22" as="geometry" />
        </mxCell>
        <mxCell id="47" parent="1" vertex="1" value="GND" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#cccccc;strokeColor=#999999;strokeWidth=2;fontSize=10;">
          <mxGeometry x="630" y="706" width="600" height="22" as="geometry" />
        </mxCell>
        <mxCell id="48" parent="1" vertex="1" value="Control signal (RESET, EN, BOOT, CLK_REQ, PWR_EN)" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#FF8C00;strokeWidth=2;fontSize=10;">
          <mxGeometry x="630" y="733" width="600" height="22" as="geometry" />
        </mxCell>
        <mxCell id="49" parent="1" vertex="1" value="Reservado / NC / deprecated" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#cccccc;strokeWidth=1;strokeDasharray=2 2;fontSize=10;">
          <mxGeometry x="630" y="760" width="600" height="22" as="geometry" />
        </mxCell>

        <mxCell id="50" parent="1" vertex="1" value="&lt;b&gt;Mapping crítico → tu carrier&lt;/b&gt;" style="text;html=1;align=center;fontSize=12;">
          <mxGeometry x="630" y="800" width="600" height="22" as="geometry" />
        </mxCell>

        <mxCell id="51" parent="1" vertex="1" value="&lt;font style=&quot;font-size:10px&quot;&gt;• &lt;b&gt;Power IN&lt;/b&gt;: paralelizar TODOS los +5V (J2 177/179/181/183/185/187)&lt;br&gt;• &lt;b&gt;BMC arbitration&lt;/b&gt;: GLOBAL_EN (118) ← open-drain OR con RTC/PD/btn&lt;br&gt;• &lt;b&gt;Recovery&lt;/b&gt;: nRPI_BOOT (110) ← USB-C mode switch · nBOOT_SELECT (108)&lt;br&gt;• &lt;b&gt;HAT auto-detect&lt;/b&gt;: AT24C256 en SDA0 (122) + SCL0 (124) → DT overlay&lt;br&gt;• &lt;b&gt;VBAT&lt;/b&gt;: pin 190 ← CR2032 (RTC backup)&lt;br&gt;• &lt;b&gt;Fan_PWM&lt;/b&gt;: pin 197 → JST PH 3-pin (5V/PWM/Tach)&lt;br&gt;&lt;br&gt;&lt;i&gt;Verificar mapping exacto contra schematic CM5_Project_20260508.pdf y datasheet CM5 oficial para señales nuevas (USB 3.0 SS)&lt;/i&gt;&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff4e6;strokeColor=#FF8C00;strokeWidth=2;fontSize=10;align=left;spacingLeft=12;verticalAlign=top;spacingTop=8;">
          <mxGeometry x="630" y="825" width="600" height="220" as="geometry" />
        </mxCell>

        <mxCell id="60" parent="1" vertex="1" value="&lt;i&gt;Fuente: Raspberry Pi CM4 Datasheet RP-008168-DS-1 · CM5 backward-compatible · status (used/free) basado en CM5_Project_20260508 schematic&lt;/i&gt;" style="text;html=1;align=center;fontSize=9;fontColor=#666666;">
          <mxGeometry x="60" y="1070" width="1740" height="30" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
'''

# Indent the grid cells to match the file
def indent(text):
    return "\n".join("        " + line if line.strip() else line for line in text.splitlines())

# Correct z-order: container BEFORE its child cells.
# HEADER ends with J1 container. Append J1 cells, THEN J2 container, THEN J2 cells, THEN middle notes.
output = HEADER + indent(j1_cells) + "\n" + J2_CONTAINER + indent(j2_cells) + "\n" + MIDDLE_NOTES

print(output)
