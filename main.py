#!/usr/bin/env python3
"""Render a deterministic one-page world-news broadsheet as entry.png."""

import os
import struct
import zlib

W = 1024
H = 1024
ENTRY_NAME = "entry.png"

PAPER = (247, 243, 234)
INK = (17, 24, 39)
NAVY = (13, 27, 62)
RED = (185, 28, 28)
BLUE = (29, 78, 216)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
CYAN = (103, 232, 249)
LIGHT = (219, 234, 254)
GRAY = (100, 116, 139)
PALE = (226, 232, 240)
WHITE = (255, 255, 255)

FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
}


class Canvas:
    def __init__(self):
        self.pixels = bytearray(W * H * 3)
        self.fill_rect(0, 0, W, H, PAPER)

    def px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.pixels[i:i + len(row)] = row

    def stroke_rect(self, x, y, w, h, color, thick=1):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(0, thick // 2)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            if r == 0:
                self.px(x, y, color)
            else:
                self.circle(x, y, r, color)

    def circle(self, cx, cy, r, color):
        r2 = r * r
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            for x in range(cx - r, cx + r + 1):
                dx = x - cx
                if dx * dx + dy * dy <= r2:
                    self.px(x, y, color)

    def ring(self, cx, cy, r, color, thick=3):
        inner = max(0, r - thick)
        outer = r + thick
        for y in range(cy - outer, cy + outer + 1):
            dy = y - cy
            for x in range(cx - outer, cx + outer + 1):
                dx = x - cx
                d2 = dx * dx + dy * dy
                if inner * inner <= d2 <= outer * outer:
                    self.px(x, y, color)

    def poly(self, points, color):
        ys = [p[1] for p in points]
        y_min = max(0, min(ys))
        y_max = min(H - 1, max(ys))
        n = len(points)
        for y in range(y_min, y_max + 1):
            nodes = []
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) // (y1 - y0)
                    nodes.append(x)
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.fill_rect(nodes[i], y, nodes[i + 1] - nodes[i] + 1, 1, color)

    def text(self, x, y, s, scale, color, bold=False):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT["?"])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "#":
                        self.fill_rect(cx + gx * scale, y + gy * scale, scale, scale, color)
                        if bold:
                            self.fill_rect(cx + gx * scale + 1, y + gy * scale, scale, scale, color)
            cx += 6 * scale
        return cx - scale

    def text_width(self, s, scale):
        if not s:
            return 0
        return len(s) * 6 * scale - scale

    def centered(self, cx, y, s, scale, color, bold=False):
        self.text(cx - self.text_width(s, scale) // 2, y, s, scale, color, bold)

    def wrap(self, s, width, scale):
        max_chars = max(1, (width + scale) // (6 * scale))
        words = s.upper().split()
        lines = []
        cur = ""
        for word in words:
            while len(word) > max_chars:
                if cur:
                    lines.append(cur)
                    cur = ""
                lines.append(word[:max_chars])
                word = word[max_chars:]
            if not cur:
                cur = word
            elif len(cur) + 1 + len(word) <= max_chars:
                cur += " " + word
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def text_box(self, x, y, width, s, scale, color, line_gap=4, bold=False, max_lines=None):
        lines = self.wrap(s, width, scale)
        if max_lines is not None:
            lines = lines[:max_lines]
        yy = y
        for line in lines:
            self.text(x, yy, line, scale, color, bold)
            yy += 7 * scale + line_gap
        return yy

    def chip(self, x, y, s, bg, fg=WHITE, scale=2):
        w = self.text_width(s, scale) + 16
        h = 7 * scale + 8
        self.fill_rect(x, y, w, h, bg)
        self.text(x + 8, y + 4, s, scale, fg, True)
        return w


def pin(c, x, y):
    c.circle(x, y, 6, RED)
    c.circle(x, y, 2, WHITE)


def draw_map(c):
    c.fill_rect(36, 560, 610, 174, LIGHT)
    c.stroke_rect(36, 560, 610, 174, INK, 2)
    c.text(56, 576, "WHERE IT HAPPENED", 2, INK, True)
    c.text(500, 576, "15 PINS", 2, RED, True)
    land = (148, 163, 184)
    c.poly([(76, 626), (150, 612), (190, 632), (172, 664), (118, 676), (82, 656)], land)
    c.poly([(154, 674), (196, 682), (188, 716), (160, 722), (146, 696)], land)
    c.poly([(292, 620), (344, 612), (366, 632), (330, 648), (298, 640)], land)
    c.poly([(318, 648), (380, 646), (402, 682), (368, 718), (330, 700), (312, 672)], land)
    c.poly([(388, 614), (500, 608), (548, 632), (520, 668), (452, 676), (402, 650)], land)
    c.poly([(512, 690), (568, 684), (586, 704), (540, 718), (514, 708)], land)
    c.line(56, 668, 626, 668, (191, 219, 254), 2)
    for x, y in [
        (118, 642), (136, 650), (232, 666), (356, 684), (382, 642),
        (172, 694), (438, 632), (452, 660), (318, 640), (548, 700),
        (420, 652), (500, 640), (586, 622), (96, 660), (286, 700),
    ]:
        pin(c, x, y)


def brief(c, x, y, width, kicker, headline, color):
    c.text(x, y, kicker, 2, color, True)
    c.text_box(x, y + 18, width, headline, 2, INK, 3, True, 3)


def bottom_story(c, x, y, kicker, headline, deck, color):
    c.fill_rect(x, y, 302, 118, WHITE)
    c.stroke_rect(x, y, 302, 118, INK, 2)
    c.fill_rect(x, y, 302, 8, color)
    c.text(x + 16, y + 16, kicker, 2, color, True)
    yy = c.text_box(x + 16, y + 36, 270, headline, 2, INK, 3, True, 2)
    c.text_box(x + 16, yy + 2, 270, deck, 2, GRAY, 3, False, 2)


def render():
    c = Canvas()
    c.stroke_rect(18, 18, 988, 988, INK, 3)
    c.stroke_rect(28, 28, 968, 968, INK, 1)

    c.centered(512, 40, "THE WORLD IN ONE PAGE", 6, INK, True)
    c.centered(512, 92, "WEDNESDAY 25 NOVEMBER 2026", 3, INK, True)
    c.centered(512, 120, "35 STORIES - 15 MAP PINS", 2, RED, True)
    c.fill_rect(36, 142, 952, 4, RED)

    stats = [
        ("175 MISSING", RED, WHITE),
        ("720,000 DEAD", WHITE, INK),
        ("NASDAQ -1.48%", WHITE, INK),
        ("MADRID 5-1", WHITE, INK),
        ("15 MAP PINS", WHITE, INK),
    ]
    for i, (label, bg, fg) in enumerate(stats):
        x = 36 + i * 192
        c.fill_rect(x, 154, 184, 44, bg)
        c.stroke_rect(x, 154, 184, 44, INK, 2)
        c.centered(x + 92, 169, label, 2, fg, True)

    c.fill_rect(36, 212, 610, 340, NAVY)
    c.fill_rect(36, 212, 610, 10, RED)
    c.chip(56, 236, "AP / CYBER", RED)
    c.text_box(56, 268, 560, "CIA SYSTEM BREACHED", 7, WHITE, 8, True, 2)
    c.text_box(56, 382, 560, "UNCLASSIFIED NETWORK HIT; ODNI ALSO AFFECTED", 3, CYAN, 5, True, 2)
    c.poly([(112, 446), (168, 428), (224, 446), (224, 508), (168, 540), (112, 508)], TEAL)
    c.line(168, 446, 150, 484, RED, 5)
    c.line(150, 484, 184, 512, RED, 5)
    c.ring(500, 478, 58, CYAN, 3)
    c.line(442, 478, 558, 478, CYAN, 2)
    c.line(500, 420, 500, 536, CYAN, 2)
    c.line(462, 438, 538, 518, CYAN, 2)
    c.line(538, 438, 462, 518, CYAN, 2)
    c.line(452, 530, 552, 428, RED, 6)
    c.text(56, 526, "NO CLASSIFIED DATA INVOLVED", 2, WHITE, True)

    c.fill_rect(666, 212, 322, 340, WHITE)
    c.stroke_rect(666, 212, 322, 340, INK, 2)
    c.text(686, 230, "TOP BRIEFS", 3, INK, True)
    brief(c, 686, 262, 282, "COURT", "HUAWEI GUILTY ON 10 OF 12 COUNTS", RED)
    c.fill_rect(686, 326, 282, 2, PALE)
    brief(c, 686, 338, 282, "ATLANTIC", "175 MIGRANTS MISSING AFTER DAKAR BOAT", BLUE)
    c.fill_rect(686, 402, 282, 2, PALE)
    brief(c, 686, 414, 282, "DR CONGO", "REBELS HALT BUNIA ADVANCE; EBOLA TEAM EVACUATED", TEAL)
    c.fill_rect(686, 486, 282, 2, PALE)
    brief(c, 686, 496, 282, "TURKEY", "MILITARY HELICOPTER CRASH KILLS FIVE", GOLD)

    draw_map(c)

    c.fill_rect(666, 560, 322, 174, INK)
    c.text(686, 574, "MARKETS + SPORT", 2, WHITE, True)
    market_lines = [
        "DELL AI SALES MORE",
        "THAN 2X; $25B BUYBACK",
        "NASDAQ -1.48%",
        "NVIDIA 31.5% SURGE BACK",
        "MADRID 5-1 PSV",
        "BELLINGHAM, MBAPPE STAR",
        "ENGLAND BEAT AUSTRALIA",
        "8 WICKETS; SERIES LEVEL",
    ]
    yy = 598
    for line in market_lines:
        c.text(686, yy, line, 2, WHITE, False)
        yy += 17

    bottom_story(c, 36, 742, "COLOMBIA", "CARTAGENA HOSTAGES FREED", "SUPERMARKET STANDOFF ENDS", BLUE)
    bottom_story(c, 361, 742, "RUSSIA", "PUTIN: REPRISAL INEVITABLE", "AFTER UKRAINE HITS OIL REFINERIES", RED)
    bottom_story(c, 686, 742, "WAR TOLL", "LEAKED NOTES PUT DEAD AT 720,000", "RUSSIAN WAR TOLL ESTIMATE", GOLD)
    bottom_story(c, 36, 868, "SPACE", "TRIPLE STAR SHOULD NOT EXIST", "FOUND 28 LIGHT-YEARS AWAY", TEAL)
    bottom_story(c, 361, 868, "PUNJAB", "BJP, AKALI DAL REUNITE", "ALLIANCE RETURNS AFTER SIX YEARS", GOLD)
    bottom_story(c, 686, 868, "IRAN", "TRUMP OFFICIALS SPLIT", "OVER TARGETING IRAN LEADERS", RED)
    return bytes(c.pixels)


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def png_bytes(pixels):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(render())
    with open(os.path.join(out_dir, ENTRY_NAME), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
