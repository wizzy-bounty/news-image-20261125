#!/usr/bin/env python3
"""News Image 20261125 entry program.

Renders one deterministic 1024x1024 PNG summarizing Wednesday
25 November 2026 world news. Python standard library only: the PNG
encoder and the bitmap font are implemented in this file. No network,
no randomness, and no time input are used.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024
MASTHEAD_SCALE = 5

PAPER = (247, 242, 231)
INK = (23, 32, 42)
MUTED = (91, 104, 116)
TEAL = (13, 92, 99)
TEAL_DARK = (9, 64, 72)
GOLD = (214, 154, 35)
RED = (190, 55, 45)
GREEN = (38, 132, 83)
BLUE = (43, 99, 171)
PURPLE = (106, 76, 166)
ORANGE = (214, 105, 35)
CARD = (255, 253, 247)
CARD_LINE = (205, 196, 178)
MAP_BG = (221, 235, 238)
LAND = (151, 190, 151)
LAND_LINE = (92, 139, 104)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "%": ["##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "·": [".....", ".....", ".....", ".##..", ".##..", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
}


class Canvas:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(color * (width * height))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, thickness=1):
        for t in range(thickness):
            self.fill_rect(x + t, y + t, w - 2 * t, 1, color)
            self.fill_rect(x + t, y + h - 1 - t, w - 2 * t, 1, color)
            self.fill_rect(x + t, y + t, 1, h - 2 * t, color)
            self.fill_rect(x + w - 1 - t, y + t, 1, h - 2 * t, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for ox in range(thickness):
                for oy in range(thickness):
                    self.set_pixel(x + ox, y + oy, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set_pixel(x, y, color)

    def circle(self, cx, cy, r, color, thickness=1):
        for y in range(cy - r - thickness, cy + r + thickness + 1):
            for x in range(cx - r - thickness, cx + r + thickness + 1):
                d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if (r - thickness) * (r - thickness) <= d <= (r + thickness) * (r + thickness):
                    self.set_pixel(x, y, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) * (x - cx)) / (rx * rx) + ((y - cy) * (y - cy)) / (ry * ry) <= 1:
                    self.set_pixel(x, y, color)

    def polygon(self, points, color):
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            for i in range(len(points)):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % len(points)]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.fill_rect(int(nodes[i]), y, max(1, int(nodes[i + 1] - nodes[i]) + 1), 1, color)

    def polygon_outline(self, points, color, thickness=1):
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            self.line(x0, y0, x1, y1, color, thickness)


def clean_text(text):
    text = text.upper().replace("’", "'").replace("−", "-").replace("–", "-").replace("—", "-")
    return "".join(ch if ch in FONT else " " for ch in text)


def text_width(text, scale):
    text = clean_text(text)
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, scale, color):
    text = clean_text(text)
    cx = x
    for ch in text:
        glyph = FONT[ch]
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "#":
                    canvas.fill_rect(cx + col_i * scale, y + row_i * scale, scale, scale, color)
        cx += 6 * scale
    return cx - scale


def draw_centered(canvas, cx, y, text, scale, color):
    return draw_text(canvas, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, max_chars):
    words = clean_text(text).split()
    lines = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(canvas, x, y, text, scale, color, max_chars, max_lines, line_gap=4):
    lines = wrap_text(text, max_chars)[:max_lines]
    for i, line in enumerate(lines):
        draw_text(canvas, x, y + i * (7 * scale + line_gap), line, scale, color)
    return y + len(lines) * (7 * scale + line_gap)


def badge(canvas, x, y, label):
    color = GREEN if label == "CONFIRMED" else ORANGE
    w = text_width(label, 1) + 12
    canvas.fill_rect(x, y, w, 15, color)
    draw_text(canvas, x + 6, y + 4, label, 1, WHITE)
    return w


def draw_icon(canvas, kind, x, y, w, h, color):
    cx = x + w // 2
    cy = y + h // 2
    if kind == "lock":
        canvas.rect(cx - 18, cy - 26, 36, 28, color, 4)
        canvas.fill_rect(cx - 28, cy - 2, 56, 34, color)
        canvas.fill_circle(cx, cy + 13, 6, WHITE)
        canvas.fill_rect(cx - 2, cy + 13, 4, 12, WHITE)
    elif kind == "court":
        canvas.polygon([(cx - 34, cy - 18), (cx, cy - 34), (cx + 34, cy - 18)], color)
        for dx in (-24, -8, 8, 24):
            canvas.fill_rect(cx + dx - 3, cy - 12, 6, 34, color)
        canvas.fill_rect(cx - 36, cy + 24, 72, 7, color)
    elif kind == "boat":
        canvas.polygon([(cx - 38, cy + 12), (cx + 38, cy + 12), (cx + 24, cy + 30), (cx - 24, cy + 30)], color)
        canvas.line(cx, cy + 10, cx, cy - 30, color, 3)
        canvas.polygon([(cx + 3, cy - 28), (cx + 3, cy + 8), (cx + 30, cy + 8)], color)
        canvas.line(cx - 38, cy + 38, cx + 38, cy + 38, BLUE, 3)
    elif kind == "shield":
        canvas.polygon([(cx, cy - 34), (cx + 28, cy - 22), (cx + 24, cy + 12), (cx, cy + 34), (cx - 24, cy + 12), (cx - 28, cy - 22)], color)
        canvas.fill_rect(cx - 4, cy - 16, 8, 32, WHITE)
        canvas.fill_rect(cx - 16, cy - 4, 32, 8, WHITE)
    elif kind == "helicopter":
        canvas.fill_ellipse(cx - 4, cy + 4, 30, 16, color)
        canvas.line(cx - 42, cy - 22, cx + 42, cy - 22, color, 3)
        canvas.line(cx, cy - 22, cx, cy - 8, color, 3)
        canvas.line(cx + 24, cy + 2, cx + 44, cy - 8, color, 4)
        canvas.line(cx - 24, cy + 24, cx + 24, cy + 24, color, 3)
    elif kind == "store":
        canvas.fill_rect(cx - 32, cy - 22, 64, 46, color)
        canvas.fill_rect(cx - 38, cy - 30, 76, 10, color)
        canvas.fill_rect(cx - 10, cy - 2, 20, 26, WHITE)
        canvas.line(cx - 22, cy + 12, cx - 12, cy + 22, WHITE, 3)
        canvas.line(cx - 12, cy + 22, cx + 12, cy - 8, WHITE, 3)
    elif kind == "flame":
        canvas.fill_rect(cx - 34, cy + 8, 68, 24, color)
        canvas.fill_rect(cx - 24, cy - 12, 12, 20, color)
        canvas.fill_rect(cx + 12, cy - 20, 12, 28, color)
        canvas.polygon([(cx, cy - 36), (cx + 16, cy - 8), (cx + 6, cy + 6), (cx - 8, cy + 6), (cx - 16, cy - 10)], RED)
    elif kind == "document":
        canvas.fill_rect(cx - 24, cy - 32, 48, 64, WHITE)
        canvas.rect(cx - 24, cy - 32, 48, 64, color, 3)
        for i, yy in enumerate(range(cy - 18, cy + 24, 10)):
            canvas.fill_rect(cx - 16, yy, 32 if i % 2 == 0 else 22, 4, color)
    elif kind == "stars":
        canvas.circle(cx, cy, 30, color, 2)
        canvas.fill_circle(cx, cy, 9, GOLD)
        canvas.fill_circle(cx - 28, cy - 14, 7, color)
        canvas.fill_circle(cx + 28, cy + 16, 7, color)
        canvas.line(cx - 28, cy - 14, cx, cy, color, 2)
        canvas.line(cx, cy, cx + 28, cy + 16, color, 2)
    elif kind == "server":
        for i in range(3):
            yy = cy - 28 + i * 20
            canvas.fill_rect(cx - 30, yy, 60, 15, color)
            canvas.fill_circle(cx + 20, yy + 7, 3, WHITE)
            canvas.fill_rect(cx - 22, yy + 5, 24, 4, WHITE)
    elif kind == "chart":
        canvas.line(cx - 34, cy + 28, cx - 34, cy - 28, color, 3)
        canvas.line(cx - 34, cy + 28, cx + 36, cy + 28, color, 3)
        canvas.line(cx - 28, cy - 18, cx - 8, cy - 4, RED, 4)
        canvas.line(cx - 8, cy - 4, cx + 8, cy - 12, RED, 4)
        canvas.line(cx + 8, cy - 12, cx + 30, cy + 16, RED, 4)
        canvas.polygon([(cx + 30, cy + 16), (cx + 18, cy + 14), (cx + 28, cy + 4)], RED)
    elif kind == "union":
        canvas.fill_circle(cx - 20, cy - 8, 16, color)
        canvas.fill_circle(cx + 20, cy - 8, 16, ORANGE)
        canvas.fill_rect(cx - 34, cy + 14, 68, 10, color)
        canvas.fill_rect(cx - 6, cy - 30, 12, 18, GOLD)
    elif kind == "ball":
        canvas.fill_circle(cx, cy, 30, WHITE)
        canvas.circle(cx, cy, 30, color, 3)
        canvas.fill_circle(cx, cy, 8, color)
        for dx, dy in ((-20, -12), (20, -12), (-16, 18), (16, 18)):
            canvas.fill_circle(cx + dx, cy + dy, 5, color)
    else:
        canvas.fill_rect(cx - 28, cy - 28, 56, 56, color)


STORIES = [
    {"n": 1, "region": "USA / INTEL", "badge": "CONFIRMED", "source": "AP", "icon": "lock", "color": TEAL, "key": "0", "headline": "CIA UNCLASSIFIED SYSTEM BREACHED; NO SECRET DATA TAKEN"},
    {"n": 2, "region": "USA / COURTS", "badge": "CONFIRMED", "source": "REUTERS", "icon": "court", "color": PURPLE, "key": "10/12", "headline": "HUAWEI GUILTY ON 10 OF 12 CRIMINAL COUNTS IN BROOKLYN"},
    {"n": 3, "region": "SENEGAL / ATLANTIC", "badge": "CONFIRMED", "source": "REUTERS", "icon": "boat", "color": BLUE, "key": "175", "headline": "ABOUT 175 MIGRANTS MISSING AFTER DAKAR BOAT LOSES CONTACT"},
    {"n": 4, "region": "DR CONGO", "badge": "CONFIRMED", "source": "BBC/WHO", "icon": "shield", "color": GREEN, "key": "BUNIA", "headline": "REBELS HALT BUNIA ADVANCE; WHO EBOLA TEAM EVACUATES"},
    {"n": 5, "region": "TURKEY", "badge": "CONFIRMED", "source": "REUTERS", "icon": "helicopter", "color": RED, "key": "5", "headline": "ESKISEHIR COPTER CRASH KILLS 5"},
    {"n": 6, "region": "COLOMBIA", "badge": "CONFIRMED", "source": "AP", "icon": "store", "color": GREEN, "key": "FREE", "headline": "CARTAGENA SUPERMARKET HOSTAGES FREED"},
    {"n": 7, "region": "RUSSIA", "badge": "REPORTED", "source": "REPORTS", "icon": "flame", "color": ORANGE, "key": "OIL", "headline": "PUTIN VOWS RETALIATION FOR REFINERY STRIKES"},
    {"n": 8, "region": "RUSSIA / WAR", "badge": "REPORTED", "source": "LEAKED RECORDS", "icon": "document", "color": RED, "key": "720K", "headline": "LEAKED RECORDS ESTIMATE 720,000 WAR DEAD"},
    {"n": 9, "region": "SPACE", "badge": "CONFIRMED", "source": "IAC", "icon": "stars", "color": PURPLE, "key": "28 LY", "headline": "IMPOSSIBLE TRIPLE STAR 28 LIGHT-YEARS AWAY"},
    {"n": 10, "region": "USA / TECH", "badge": "CONFIRMED", "source": "BARRON'S", "icon": "server", "color": TEAL, "key": "$25B", "headline": "DELL AI SERVER SALES DOUBLE; $25B BUYBACK"},
    {"n": 11, "region": "USA / MARKETS", "badge": "CONFIRMED", "source": "REUTERS", "icon": "chart", "color": RED, "key": "-1.48%", "headline": "NASDAQ -1.48% AS NVIDIA GIVES BACK 31.5% SURGE"},
    {"n": 12, "region": "INDIA", "badge": "CONFIRMED", "source": "TIMES OF INDIA", "icon": "union", "color": ORANGE, "key": "PUNJAB", "headline": "BJP AND AKALI DAL REUNITE FOR PUNJAB ELECTION"},
    {"n": 13, "region": "SPAIN", "badge": "CONFIRMED", "source": "MATCH REPORT", "icon": "ball", "color": BLUE, "key": "5-1", "headline": "REAL MADRID 5-1 PSV"},
]

ALSO = [
    "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN T20",
    "TRUMP OFFICIALS SPLIT OVER IRAN",
    "HOUTHI DRONE HITS RIYADH TOWER; 11 HURT",
    "THANKSGIVING TRAVEL CHAOS AT O'HARE",
    "MODI-MERZ DEEPEN INDIA-GERMANY TIES",
    "MEDICINE SHORTAGES IN IRAN",
    "NATO PREPARES EARLY-WARNING AIRCRAFT IN POLAND",
    "VENEZUELA PUBLIC DEBT $237.5B",
]

DATE_CHECK = [
    "SOORYAVANSHI 204-RUN CRICKET WIN - 24 NOV",
    "NEPAL 5.3 EARTHQUAKE - 24 NOV",
    "LANDMINE MONITOR REPORT - 24 NOV",
]


def draw_lead(canvas, story, x, y, w, h):
    canvas.fill_rect(x, y, w, h, CARD)
    canvas.rect(x, y, w, h, CARD_LINE, 2)
    canvas.fill_rect(x, y, w, 8, story["color"])
    canvas.fill_rect(x + 10, y + 16, w - 20, 86, (238, 243, 240))
    draw_icon(canvas, story["icon"], x + 18, y + 22, 92, 74, story["color"])
    key = story["key"]
    scale = 4 if len(key) <= 4 else 3
    draw_text(canvas, x + w - 18 - text_width(key, scale), y + 42, key, scale, story["color"])
    canvas.fill_circle(x + 24, y + 118, 13, story["color"])
    draw_centered(canvas, x + 24, y + 114, str(story["n"]), 1, WHITE)
    draw_text(canvas, x + 44, y + 114, story["region"], 1, MUTED)
    badge_w = text_width(story["badge"], 1) + 12
    badge(canvas, x + w - 12 - badge_w, y + 110, story["badge"])
    draw_wrapped(canvas, x + 12, y + 136, story["headline"], 2, INK, 24, 4, 5)
    draw_text(canvas, x + 12, y + h - 22, "SOURCE: " + story["source"], 1, MUTED)


def draw_medium(canvas, story, x, y, w, h):
    canvas.fill_rect(x, y, w, h, CARD)
    canvas.rect(x, y, w, h, CARD_LINE, 2)
    canvas.fill_rect(x + 8, y + 8, w - 16, 48, (238, 243, 240))
    draw_icon(canvas, story["icon"], x + 10, y + 10, 58, 44, story["color"])
    key = story["key"]
    scale = 3 if len(key) <= 5 else 2
    draw_text(canvas, x + w - 10 - text_width(key, scale), y + 22, key, scale, story["color"])
    canvas.fill_circle(x + 16, y + 68, 10, story["color"])
    draw_centered(canvas, x + 16, y + 65, str(story["n"]), 1, WHITE)
    draw_text(canvas, x + 31, y + 65, story["region"], 1, MUTED)
    badge_w = text_width(story["badge"], 1) + 12
    badge(canvas, x + w - 8 - badge_w, y + 61, story["badge"])
    draw_wrapped(canvas, x + 8, y + 82, story["headline"], 2, INK, 14, 4, 2)
    draw_text(canvas, x + 8, y + h - 13, "SOURCE: " + story["source"], 1, MUTED)


def draw_map(canvas, x, y, w, h):
    canvas.fill_rect(x, y, w, h, MAP_BG)
    canvas.rect(x, y, w, h, TEAL_DARK, 2)
    draw_text(canvas, x + 10, y + 8, "WORLD MAP", 2, TEAL_DARK)
    draw_text(canvas, x + 150, y + 12, "PINS MATCH STORY NUMBERS", 1, MUTED)
    ox, oy = x + 18, y + 34
    mw, mh = w - 36, h - 48
    continents = [
        [(20, 25), (120, 12), (190, 28), (175, 62), (120, 78), (75, 66), (35, 82), (18, 48)],
        [(105, 88), (150, 82), (172, 112), (150, 146), (122, 132), (104, 108)],
        [(245, 30), (300, 18), (330, 42), (305, 62), (262, 58), (238, 46)],
        [(252, 68), (310, 62), (338, 88), (318, 128), (282, 140), (258, 105)],
        [(330, 24), (470, 10), (545, 28), (520, 62), (455, 58), (410, 78), (350, 62)],
        [(455, 82), (510, 78), (535, 104), (500, 126), (462, 112)],
        [(500, 126), (548, 122), (560, 140), (522, 146), (498, 138)],
    ]
    for poly in continents:
        pts = [(ox + int(px * mw / 580), oy + int(py * mh / 160)) for px, py in poly]
        canvas.polygon(pts, LAND)
        canvas.polygon_outline(pts, LAND_LINE, 1)
    pins = {
        1: (145, 45), 2: (172, 50), 3: (252, 92), 4: (302, 105), 5: (345, 58),
        6: (142, 104), 7: (430, 34), 8: (462, 48), 9: (520, 24), 10: (112, 62),
        11: (205, 72), 12: (438, 88), 13: (282, 58),
    }
    for n, (px, py) in pins.items():
        cx = ox + int(px * mw / 580)
        cy = oy + int(py * mh / 160)
        canvas.fill_circle(cx, cy, 11, RED)
        canvas.circle(cx, cy, 11, WHITE, 1)
        draw_centered(canvas, cx, cy - 3, str(n), 1, WHITE)


def render():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    canvas.fill_rect(0, 0, WIDTH, 10, TEAL_DARK)
    draw_centered(canvas, WIDTH // 2, 18, "WEDNESDAY 25 NOVEMBER 2026", MASTHEAD_SCALE, INK)
    canvas.fill_rect(24, 64, 976, 34, TEAL_DARK)
    draw_centered(canvas, WIDTH // 2, 72, "35 STORIES · 15 MAP PINS", 3, WHITE)

    lead_y = 112
    lead_w = 317
    for i, story in enumerate(STORIES[:3]):
        draw_lead(canvas, story, 24 + i * (lead_w + 12), lead_y, lead_w, 248)

    med_y = 372
    med_w = 188
    med_h = 164
    for i, story in enumerate(STORIES[3:]):
        col = i % 5
        row = i // 5
        draw_medium(canvas, story, 24 + col * (med_w + 8), med_y + row * (med_h + 10), med_w, med_h)

    draw_map(canvas, 24, 722, 608, 188)

    also_x, also_y, also_w = 648, 722, 352
    canvas.fill_rect(also_x, also_y, also_w, 116, CARD)
    canvas.rect(also_x, also_y, also_w, 116, CARD_LINE, 2)
    canvas.fill_rect(also_x, also_y, also_w, 24, GOLD)
    draw_text(canvas, also_x + 10, also_y + 6, "ALSO ON WEDNESDAY", 2, INK)
    yy = also_y + 31
    for item in ALSO:
        canvas.fill_rect(also_x + 10, yy + 2, 5, 5, TEAL)
        yy = draw_wrapped(canvas, also_x + 22, yy, item, 1, INK, 52, 1, 0) + 3

    dc_y = 846
    canvas.fill_rect(also_x, dc_y, also_w, 64, (255, 244, 214))
    canvas.rect(also_x, dc_y, also_w, 64, GOLD, 2)
    draw_text(canvas, also_x + 10, dc_y + 6, "DATE CHECK - EXCLUDED", 2, INK)
    yy = dc_y + 27
    for item in DATE_CHECK:
        canvas.fill_rect(also_x + 10, yy + 2, 5, 5, RED)
        draw_text(canvas, also_x + 22, yy, item, 1, INK)
        yy += 11

    canvas.fill_rect(24, 918, 976, 82, INK)
    draw_centered(canvas, WIDTH // 2, 930, "SOURCES: AP · REUTERS · BBC/WHO · IAC · BARRON'S · TIMES OF INDIA", 2, WHITE)
    draw_centered(canvas, WIDTH // 2, 958, "ONE IMAGE SUMMARY OF WEDNESDAY 25 NOVEMBER 2026", 2, (210, 220, 226))
    return canvas


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw.extend(canvas.pixels[start:start + stride])
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b"")


def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    data = encode_png(render())
    with open(os.path.join(output_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
