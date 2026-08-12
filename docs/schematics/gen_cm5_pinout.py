"""Generate drawio XML cells for CM5 J1/J2 pinout grids.

Each pin = one colored cell with the signal name + pin number.
Color = signal class. Border style = assignment status in CM5_Project carrier.
"""

# Signal class colors
COLORS = {
    "gnd":     ("#cccccc", "#999999"),  # gray
    "power":   ("#fff2cc", "#d6b656"),  # yellow
    "hs":      ("#e1d5e7", "#9673a6"),  # purple (high-speed diff pairs)
    "gpio":    ("#d5e8d4", "#82b366"),  # green
    "ctrl":    ("#ffe6cc", "#FF8C00"),  # orange
    "i2c":     ("#d5e8d4", "#82b366"),  # green
    "nc":      ("#f5f5f5", "#cccccc"),  # light gray
}

# (pin_number, signal_name, class, status)
# status: "used" = solid border (assigned in carrier), "free" = dashed border, "req" = required
# CM5_Project carrier uses: Ethernet, USB2, PCIe, HDMI0, I2C0, control signals, +5V, GND
# Free/unused: CAM1, DSI0/1, HDMI1, SD-alternate, deprecated

J1 = [
    (1, "GND", "gnd", "req"), (2, "GND", "gnd", "req"),
    (3, "ETH_TX_P3", "hs", "used"), (4, "+3V3", "power", "req"),
    (5, "ETH_TX_N3", "hs", "used"), (6, "+3V3", "power", "req"),
    (7, "ETH_TX_N2", "hs", "used"), (8, "GND", "gnd", "req"),
    (9, "ETH_TX_P2", "hs", "used"), (10, "EEPROM_nWP", "ctrl", "free"),
    (11, "GND", "gnd", "req"), (12, "ETH_SYNC_OUT", "ctrl", "free"),
    (13, "ETH_TX_P1", "hs", "used"), (14, "NC", "nc", "free"),
    (15, "ETH_TX_N1", "hs", "used"), (16, "ETH_SYNC_IN", "ctrl", "free"),
    (17, "GND", "gnd", "req"), (18, "ETH_n_LED1", "gpio", "used"),
    (19, "ETH_TX_N0", "hs", "used"), (20, "ETH_n_LED2", "gpio", "used"),
    (21, "ETH_TX_P0", "hs", "used"), (22, "GND", "gnd", "req"),
    (23, "GND", "gnd", "req"), (24, "CAM1_D0_N", "hs", "free"),
    (25, "GPIO0 UART2_TX", "gpio", "used"), (26, "CAM1_D0_P", "hs", "free"),
    (27, "GPIO1 UART2_RX", "gpio", "used"), (28, "GND", "gnd", "req"),
    (29, "GPIO2 SDA1", "i2c", "used"), (30, "CAM1_D1_N", "hs", "free"),
    (31, "GND", "gnd", "req"), (32, "CAM1_D1_P", "hs", "free"),
    (33, "GPIO3 SCL1", "i2c", "used"), (34, "GND", "gnd", "req"),
    (35, "GPIO4 UART3_TX", "gpio", "used"), (36, "CAM1_C_N", "hs", "free"),
    (37, "GPIO5 UART3_RX", "gpio", "used"), (38, "CAM1_C_P", "hs", "free"),
    (39, "GND", "gnd", "req"), (40, "GND", "gnd", "req"),
    (41, "GPIO6", "gpio", "free"), (42, "CAM1_D2_N", "hs", "free"),
    (43, "GPIO7 SPI0_CE1", "gpio", "used"), (44, "CAM1_D2_P", "hs", "free"),
    (45, "GPIO8 SPI0_CE0", "gpio", "used"), (46, "GND", "gnd", "req"),
    (47, "GPIO9 SPI0_MISO", "gpio", "used"), (48, "CAM1_D3_N", "hs", "free"),
    (49, "GND", "gnd", "req"), (50, "CAM1_D3_P", "hs", "free"),
    (51, "GPIO10 SPI0_MOSI", "gpio", "used"), (52, "GND", "gnd", "req"),
    (53, "GPIO11 SPI0_SCLK", "gpio", "used"), (54, "DSI1_D0_N", "hs", "free"),
    (55, "GPIO12", "gpio", "free"), (56, "DSI1_D0_P", "hs", "free"),
    (57, "GPIO13", "gpio", "free"), (58, "GND", "gnd", "req"),
    (59, "GND", "gnd", "req"), (60, "DSI1_D1_N", "hs", "free"),
    (61, "GPIO14 UART0_TX", "gpio", "used"), (62, "DSI1_D1_P", "hs", "free"),
    (63, "GPIO15 UART0_RX", "gpio", "used"), (64, "GND", "gnd", "req"),
    (65, "GPIO16 SPI1_CE2", "gpio", "used"), (66, "DSI1_C_N", "hs", "free"),
    (67, "GPIO17 SPI1_CE1", "gpio", "used"), (68, "DSI1_C_P", "hs", "free"),
    (69, "GND", "gnd", "req"), (70, "GND", "gnd", "req"),
    (71, "GPIO18 SPI1_CE0", "gpio", "used"), (72, "DSI1_D2_N", "hs", "free"),
    (73, "GPIO19 SPI1_MISO", "gpio", "used"), (74, "DSI1_D2_P", "hs", "free"),
    (75, "GPIO20 SPI1_MOSI", "gpio", "used"), (76, "GND", "gnd", "req"),
    (77, "GPIO21 SPI1_SCLK", "gpio", "used"), (78, "DSI1_D3_N", "hs", "free"),
    (79, "GND", "gnd", "req"), (80, "DSI1_D3_P", "hs", "free"),
    (81, "GPIO22 RS485_DE", "gpio", "used"), (82, "GND", "gnd", "req"),
    (83, "GPIO23 BMC_IRQ", "gpio", "used"), (84, "DSI0_D0_N", "hs", "free"),
    (85, "GPIO24 nRPIBOOT", "gpio", "used"), (86, "DSI0_D0_P", "hs", "free"),
    (87, "GND", "gnd", "req"), (88, "GND", "gnd", "req"),
    (89, "GPIO25 Buzzer", "gpio", "used"), (90, "DSI0_D1_N", "hs", "free"),
    (91, "GPIO26 USR_BTN", "gpio", "used"), (92, "DSI0_D1_P", "hs", "free"),
    (93, "GPIO27 Heartbeat", "gpio", "used"), (94, "GND", "gnd", "req"),
    (95, "GND", "gnd", "req"), (96, "DSI0_C_N", "hs", "free"),
    (97, "SDX_VDD_OVR", "ctrl", "free"), (98, "DSI0_C_P", "hs", "free"),
    (99, "SDIO_VDDIO_TRK", "ctrl", "free"), (100, "GND", "gnd", "req"),
]

J2 = [
    (101, "USB2_OTG_ID", "ctrl", "used"), (102, "PCIE_CLK_REQ_n", "ctrl", "used"),
    (103, "USB2_DP", "hs", "used"), (104, "GND", "gnd", "req"),
    (105, "USB2_DN", "hs", "used"), (106, "PCIE_PWR_EN", "ctrl", "used"),
    (107, "GND", "gnd", "req"), (108, "nBOOT_SELECT", "ctrl", "used"),
    (109, "PCIE_REF_CLK_P", "hs", "used"), (110, "nRPI_BOOT", "ctrl", "used"),
    (111, "PCIE_REF_CLK_N", "hs", "used"), (112, "nUSB_BOOT", "ctrl", "free"),
    (113, "GND", "gnd", "req"), (114, "NC", "nc", "free"),
    (115, "PCIE_RX_N", "hs", "used"), (116, "RUN_PG", "ctrl", "used"),
    (117, "PCIE_RX_P", "hs", "used"), (118, "GLOBAL_EN", "ctrl", "used"),
    (119, "GND", "gnd", "req"), (120, "nEXTRST", "ctrl", "used"),
    (121, "PCIE_TX_N", "hs", "used"), (122, "SDA0 HAT_EEPROM", "i2c", "used"),
    (123, "PCIE_TX_P", "hs", "used"), (124, "SCL0 HAT_EEPROM", "i2c", "used"),
    (125, "GND", "gnd", "req"), (126, "SD_PWR_ON", "ctrl", "free"),
    (127, "CAM_GPIO", "gpio", "free"), (128, "VDAC_COMP", "ctrl", "free"),
    (129, "nPCIE_RST", "ctrl", "used"), (130, "NC", "nc", "free"),
    (131, "GND", "gnd", "req"), (132, "HDMI1_TX2_P", "hs", "free"),
    (133, "NC", "nc", "free"), (134, "HDMI1_TX2_N", "hs", "free"),
    (135, "HDMI0_HOTPLUG", "ctrl", "used"), (136, "GND", "gnd", "req"),
    (137, "HDMI0_SDA", "i2c", "used"), (138, "HDMI1_TX1_P", "hs", "free"),
    (139, "HDMI0_SCL", "i2c", "used"), (140, "HDMI1_TX1_N", "hs", "free"),
    (141, "HDMI0_CEC", "ctrl", "used"), (142, "GND", "gnd", "req"),
    (143, "HDMI0_TX2_P", "hs", "used"), (144, "HDMI1_TX0_P", "hs", "free"),
    (145, "HDMI0_TX2_N", "hs", "used"), (146, "HDMI1_TX0_N", "hs", "free"),
    (147, "GND", "gnd", "req"), (148, "GND", "gnd", "req"),
    (149, "HDMI0_TX1_P", "hs", "used"), (150, "HDMI1_CK_P", "hs", "free"),
    (151, "HDMI0_TX1_N", "hs", "used"), (152, "HDMI1_CK_N", "hs", "free"),
    (153, "GND", "gnd", "req"), (154, "GND", "gnd", "req"),
    (155, "HDMI0_TX0_P", "hs", "used"), (156, "HDMI1_HOTPLUG", "ctrl", "free"),
    (157, "HDMI0_TX0_N", "hs", "used"), (158, "HDMI1_SDA", "i2c", "free"),
    (159, "GND", "gnd", "req"), (160, "HDMI1_SCL", "i2c", "free"),
    (161, "HDMI0_CK_P", "hs", "used"), (162, "HDMI1_CEC", "ctrl", "free"),
    (163, "HDMI0_CK_N", "hs", "used"), (164, "NC", "nc", "free"),
    (165, "GND", "gnd", "req"), (166, "NC", "nc", "free"),
    (167, "SD_DAT0", "gpio", "free"), (168, "NC", "nc", "free"),
    (169, "SD_DAT1", "gpio", "free"), (170, "NC", "nc", "free"),
    (171, "SD_DAT2", "gpio", "free"), (172, "SD_CLK", "gpio", "free"),
    (173, "SD_DAT3", "gpio", "free"), (174, "SD_CMD", "gpio", "free"),
    (175, "GND", "gnd", "req"), (176, "NC", "nc", "free"),
    (177, "+5V", "power", "used"), (178, "NC", "nc", "free"),
    (179, "+5V", "power", "used"), (180, "NC", "nc", "free"),
    (181, "+5V", "power", "used"), (182, "deprec", "nc", "free"),
    (183, "+5V", "power", "used"), (184, "deprec", "nc", "free"),
    (185, "+5V", "power", "used"), (186, "deprec", "nc", "free"),
    (187, "+5V", "power", "used"), (188, "deprec", "nc", "free"),
    (189, "GND", "gnd", "req"), (190, "VBAT_RTC", "power", "used"),
    (191, "+1V8_VREF", "nc", "free"), (192, "NC", "nc", "free"),
    (193, "NC", "nc", "free"), (194, "NC", "nc", "free"),
    (195, "GND", "gnd", "req"), (196, "NC", "nc", "free"),
    (197, "Fan_PWM", "gpio", "used"), (198, "NC", "nc", "free"),
    (199, "NC", "nc", "free"), (200, "NC", "nc", "free"),
]


def cell(cell_id, x, y, w, h, label, fill, stroke, dashed, fontsize=7):
    border_style = "strokeWidth=2;" if not dashed else "strokeWidth=1;strokeDasharray=2 2;"
    return (f'<mxCell id="p{cell_id}" parent="1" vertex="1" '
            f'value="{label}" '
            f'style="rounded=0;whiteSpace=wrap;html=1;fillColor={fill};'
            f'strokeColor={stroke};{border_style}'
            f'fontSize={fontsize};fontFamily=Consolas;align=center;verticalAlign=middle;">\n'
            f'  <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'</mxCell>')


def pin_label(cell_id, x, y, num):
    return (f'<mxCell id="n{cell_id}" parent="1" vertex="1" value="{num}" '
            f'style="text;html=1;align=center;verticalAlign=middle;fontSize=8;'
            f'fontFamily=Consolas;fontStyle=1;">\n'
            f'  <mxGeometry x="{x}" y="{y}" width="22" height="16" as="geometry" />\n'
            f'</mxCell>')


def build_grid(pins, x_origin, y_origin, label_prefix):
    """Build 50 rows × (sig_left, pin_left, pin_right, sig_right) grid."""
    out = []
    cell_w = 130
    cell_h = 16
    pin_col_w = 22

    # column header row
    header_y = y_origin - 22
    out.append(f'<mxCell id="hdr_{label_prefix}_L" parent="1" vertex="1" '
               f'value="&lt;b&gt;Signal&lt;/b&gt;" '
               f'style="text;html=1;align=center;fontSize=9;">\n'
               f'  <mxGeometry x="{x_origin}" y="{header_y}" '
               f'width="{cell_w}" height="18" as="geometry" />\n'
               f'</mxCell>')
    out.append(f'<mxCell id="hdr_{label_prefix}_PL" parent="1" vertex="1" '
               f'value="&lt;b&gt;Pin&lt;/b&gt;" '
               f'style="text;html=1;align=center;fontSize=9;">\n'
               f'  <mxGeometry x="{x_origin + cell_w}" y="{header_y}" '
               f'width="{pin_col_w}" height="18" as="geometry" />\n'
               f'</mxCell>')
    out.append(f'<mxCell id="hdr_{label_prefix}_PR" parent="1" vertex="1" '
               f'value="&lt;b&gt;Pin&lt;/b&gt;" '
               f'style="text;html=1;align=center;fontSize=9;">\n'
               f'  <mxGeometry x="{x_origin + cell_w + pin_col_w}" y="{header_y}" '
               f'width="{pin_col_w}" height="18" as="geometry" />\n'
               f'</mxCell>')
    out.append(f'<mxCell id="hdr_{label_prefix}_R" parent="1" vertex="1" '
               f'value="&lt;b&gt;Signal&lt;/b&gt;" '
               f'style="text;html=1;align=center;fontSize=9;">\n'
               f'  <mxGeometry x="{x_origin + cell_w + 2 * pin_col_w}" y="{header_y}" '
               f'width="{cell_w}" height="18" as="geometry" />\n'
               f'</mxCell>')

    # 50 rows
    for i in range(0, len(pins), 2):
        left_pin = pins[i]
        right_pin = pins[i + 1]
        y = y_origin + (i // 2) * cell_h

        # left signal cell
        fill_l, stroke_l = COLORS[left_pin[2]]
        dashed_l = left_pin[3] == "free"
        out.append(cell(left_pin[0], x_origin, y, cell_w, cell_h,
                        left_pin[1], fill_l, stroke_l, dashed_l))

        # left pin number
        out.append(pin_label(left_pin[0], x_origin + cell_w, y, left_pin[0]))

        # right pin number
        out.append(pin_label(right_pin[0], x_origin + cell_w + pin_col_w, y, right_pin[0]))

        # right signal cell
        fill_r, stroke_r = COLORS[right_pin[2]]
        dashed_r = right_pin[3] == "free"
        out.append(cell(right_pin[0], x_origin + cell_w + 2 * pin_col_w, y, cell_w, cell_h,
                        right_pin[1], fill_r, stroke_r, dashed_r))

    return "\n".join(out)


if __name__ == "__main__":
    # J1 grid at x=110, y=220 (inside the J1 container at x=60..1140, y=120..1300)
    j1_xml = build_grid(J1, 110, 230, "j1")
    # J2 grid at x=1310, y=220
    j2_xml = build_grid(J2, 1310, 230, "j2")

    print(j1_xml)
    print()
    print(j2_xml)
