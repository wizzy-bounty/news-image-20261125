#!/usr/bin/env python3
"""News Image 20261125 - one-image world news summary for Wednesday 25 Nov 2026.

Deterministic stdlib-only renderer. Draws at 2048x2048 and box-downsamples to
1024x1024 for smooth edges, then writes a PNG with a hand-rolled encoder.
No network, no randomness, no clock reads: two runs are byte-identical.
"""

import os
import struct
import zlib
from pathlib import Path

SS = 2
W = 1024
H = 1024
CW = W * SS
CH = H * SS

INK = (24, 26, 34)
PAPER = (247, 243, 234)
RED = (178, 34, 44)
NAVY = (18, 38, 74)
TEAL = (10, 110, 120)
GOLD = (214, 154, 32)
GREEN = (38, 128, 74)
SKY = (126, 184, 224)
SAND = (222, 198, 150)
GREY = (96, 100, 110)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000",) * 7,
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "·": ("00000", "00000", "00000", "01100", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
}

canvas = bytearray(bytes(PAPER) * (CW * CH))


def px(x, y, color):
    if 0 <= x < CW and 0 <= y < CH:
        i = (y * CW + x) * 3
        canvas[i:i + 3] = bytes(color)


def rect(x, y, w, h, color):
    x0, y0 = int(x * SS), int(y * SS)
    x1, y1 = int((x + w) * SS), int((y + h) * SS)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(CW, x1), min(CH, y1)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * CW + x0) * 3
        canvas[i:i + len(row)] = row


def vgrad(x, y, w, h, top, bottom):
    steps = int(h * SS)
    for s in range(steps):
        t = s / max(1, steps - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        rect(x, y + s / SS, w, 1 / SS, c)


def circle(cx, cy, r, color):
    cxp, cyp, rp = cx * SS, cy * SS, r * SS
    y0, y1 = int(cyp - rp), int(cyp + rp)
    for yy in range(max(0, y0), min(CH, y1 + 1)):
        dy = yy - cyp
        span = rp * rp - dy * dy
        if span < 0:
            continue
        dx = int(span ** 0.5)
        x0 = max(0, int(cxp - dx))
        x1 = min(CW, int(cxp + dx) + 1)
        row = bytes(color) * (x1 - x0)
        i = (yy * CW + x0) * 3
        canvas[i:i + len(row)] = row


def ellipse(cx, cy, rx, ry, color):
    cxp, cyp = cx * SS, cy * SS
    rxp, ryp = rx * SS, ry * SS
    y0, y1 = int(cyp - ryp), int(cyp + ryp)
    for yy in range(max(0, y0), min(CH, y1 + 1)):
        dy = (yy - cyp) / ryp
        span = 1 - dy * dy
        if span < 0:
            continue
        dx = int(rxp * (span ** 0.5))
        x0 = max(0, int(cxp - dx))
        x1 = min(CW, int(cxp + dx) + 1)
        row = bytes(color) * (x1 - x0)
        i = (yy * CW + x0) * 3
        canvas[i:i + len(row)] = row


def line(x0, y0, x1, y1, color, thick=1.6):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * SS) + 1
    r = max(1, int(thick * SS / 2))
    for s in range(steps + 1):
        t = s / steps
        cx = int((x0 + (x1 - x0) * t) * SS)
        cy = int((y0 + (y1 - y0) * t) * SS)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                px(xx, yy, color)


def tri(x0, y0, x1, y1, x2, y2, color):
    miny, maxy = int(min(y0, y1, y2) * SS), int(max(y0, y1, y2) * SS)
    pts = [(x0 * SS, y0 * SS), (x1 * SS, y1 * SS), (x2 * SS, y2 * SS)]

    def edge(ax, ay, bx, by, yy):
        if by == ay:
            return None
        t = (yy - ay) / (by - ay)
        if 0 <= t <= 1:
            return ax + (bx - ax) * t
        return None

    for yy in range(max(0, miny), min(CH, maxy + 1)):
        xs = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            v = edge(pts[a][0], pts[a][1], pts[b][0], pts[b][1], yy)
            if v is not None:
                xs.append(v)
        if len(xs) >= 2:
            xlo, xhi = int(min(xs)), int(max(xs))
            xlo, xhi = max(0, xlo), min(CW - 1, xhi)
            row = bytes(color) * (xhi - xlo + 1)
            i = (yy * CW + xlo) * 3
            canvas[i:i + len(row)] = row


def text_w(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT["?"])
        for r, rowbits in enumerate(glyph):
            for c, bit in enumerate(rowbits):
                if bit == "1":
                    rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx - scale


def draw_text_c(cx, y, text, scale, color):
    draw_text(cx - text_w(text, scale) / 2, y, text, scale, color)


def wrap_lines(text, scale, max_w):
    words = text.upper().split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrap(x, y, text, scale, color, max_w, leading=None):
    leading = leading or (8 * scale)
    for i, ln in enumerate(wrap_lines(text, scale, max_w)):
        draw_text(x, y + i * leading, ln, scale, color)
    return y + len(wrap_lines(text, scale, max_w)) * leading


def star(cx, cy, r, color):
    tri(cx, cy - r, cx - r * 0.32, cy + r * 0.3, cx + r * 0.32, cy + r * 0.3, color)
    tri(cx - r, cy - r * 0.15, cx + r, cy - r * 0.15, cx, cy + r, color)


def _sin(t):
    import math
    return math.sin(t)


def _cos(t):
    import math
    return math.cos(t)


def scene(kind, x, y, w, h):
    """Multi-shape pictogram scenes inside box (x, y, w, h)."""
    if kind == "cia":
        vgrad(x, y, w, h, (16, 24, 52), (44, 70, 130))
        for i in range(3):
            bx = x + 12 + i * (w / 3)
            rect(bx, y + h * 0.25, w / 3 - 16, h * 0.65, (70, 90, 130))
            for r in range(4):
                rect(bx + 5, y + h * 0.32 + r * h * 0.14, w / 3 - 26, 3, (140, 220, 255))
        tri(x + w * 0.56, y + h * 0.08, x + w * 0.44, y + h * 0.52, x + w * 0.54, y + h * 0.52, GOLD)
        tri(x + w * 0.54, y + h * 0.46, x + w * 0.42, y + h * 0.9, x + w * 0.62, y + h * 0.4, GOLD)
    elif kind == "huawei":
        vgrad(x, y, w, h, (240, 226, 190), (214, 188, 140))
        rect(x + w * 0.18, y + h * 0.34, w * 0.64, h * 0.5, (120, 96, 64))
        tri(x + w * 0.12, y + h * 0.34, x + w * 0.88, y + h * 0.34, x + w * 0.5, y + h * 0.12, (84, 62, 40))
        for i in range(4):
            rect(x + w * (0.26 + i * 0.15), y + h * 0.42, 6, h * 0.34, (240, 230, 200))
        line(x + w * 0.62, y + h * 0.62, x + w * 0.82, y + h * 0.42, (60, 40, 24), 5)
        rect(x + w * 0.76, y + h * 0.3, w * 0.14, h * 0.12, (60, 40, 24))
    elif kind == "migrants":
        vgrad(x, y, w, h * 0.55, (250, 200, 120), (250, 150, 90))
        circle(x + w * 0.78, y + h * 0.26, h * 0.14, (255, 220, 120))
        vgrad(x, y + h * 0.5, w, h * 0.5, (30, 110, 160), (14, 60, 110))
        for i in range(5):
            wy = y + h * (0.58 + i * 0.09)
            for s in range(6):
                line(x + 8 + s * w / 6, wy, x + 22 + s * w / 6, wy - 3, (170, 220, 250), 1.6)
        tri(x + w * 0.3, y + h * 0.62, x + w * 0.72, y + h * 0.62, x + w * 0.62, y + h * 0.76, (90, 58, 30))
        rect(x + w * 0.48, y + h * 0.34, 3, h * 0.28, (70, 46, 24))
        tri(x + w * 0.51, y + h * 0.36, x + w * 0.51, y + h * 0.6, x + w * 0.66, y + h * 0.6, WHITE)
    elif kind == "congo":
        vgrad(x, y, w, h, (200, 226, 190), (150, 196, 140))
        rect(x + w * 0.36, y + h * 0.22, w * 0.28, h * 0.56, WHITE)
        rect(x + w * 0.46, y + h * 0.3, w * 0.08, h * 0.4, RED)
        rect(x + w * 0.4, y + h * 0.44, w * 0.2, h * 0.1, RED)
        line(x + w * 0.08, y + h * 0.5, x + w * 0.3, y + h * 0.5, NAVY, 4)
        tri(x + w * 0.3, y + h * 0.42, x + w * 0.3, y + h * 0.58, x + w * 0.18, y + h * 0.5, NAVY)
    elif kind == "copter":
        vgrad(x, y, w, h, (170, 205, 235), (220, 235, 250))
        line(x + w * 0.15, y + h * 0.2, x + w * 0.85, y + h * 0.2, INK, 2.4)
        rect(x + w * 0.48, y + h * 0.2, 3, h * 0.1, INK)
        ellipse(x + w * 0.5, y + h * 0.48, w * 0.2, h * 0.16, (70, 110, 70))
        line(x + w * 0.68, y + h * 0.46, x + w * 0.92, y + h * 0.36, (70, 110, 70), 4)
        line(x + w * 0.92, y + h * 0.28, x + w * 0.92, y + h * 0.46, INK, 2.4)
        circle(x + w * 0.44, y + h * 0.46, h * 0.07, SKY)
        line(x + w * 0.36, y + h * 0.66, x + w * 0.64, y + h * 0.66, INK, 2.4)
    elif kind == "hostages":
        vgrad(x, y, w, h, (240, 230, 210), (220, 200, 170))
        rect(x + w * 0.16, y + h * 0.3, w * 0.68, h * 0.52, (160, 120, 80))
        rect(x + w * 0.16, y + h * 0.22, w * 0.68, h * 0.1, RED)
        rect(x + w * 0.44, y + h * 0.48, w * 0.14, h * 0.34, (60, 40, 24))
        line(x + w * 0.72, y + h * 0.6, x + w * 0.8, y + h * 0.68, GREEN, 3.4)
        line(x + w * 0.8, y + h * 0.68, x + w * 0.92, y + h * 0.46, GREEN, 3.4)
    elif kind == "putin":
        vgrad(x, y, w, h, (60, 50, 70), (110, 80, 90))
        for i in range(3):
            bx = x + w * (0.2 + i * 0.24)
            rect(bx, y + h * 0.34, w * 0.1, h * 0.5, (140, 140, 150))
            circle(bx + w * 0.05, y + h * 0.26, h * 0.09, (200, 200, 205))
        tri(x + w * 0.5, y + h * 0.08, x + w * 0.4, y + h * 0.3, x + w * 0.6, y + h * 0.3, (240, 120, 40))
        circle(x + w * 0.5, y + h * 0.24, h * 0.07, GOLD)
    elif kind == "war":
        vgrad(x, y, w, h, (30, 30, 40), (70, 60, 70))
        heights = (0.3, 0.45, 0.6, 0.82)
        for i, hh in enumerate(heights):
            rect(x + w * (0.14 + i * 0.2), y + h * (0.88 - hh), w * 0.12, h * hh, RED if i == 3 else (150, 150, 160))
        line(x + w * 0.1, y + h * 0.88, x + w * 0.92, y + h * 0.88, WHITE, 2)
    elif kind == "stars":
        vgrad(x, y, w, h, (8, 10, 34), (30, 30, 80))
        for i in range(14):
            px(int((x + (i * 37) % int(w)) * SS), int((y + (i * 23) % int(h)) * SS), WHITE)
        star(x + w * 0.42, y + h * 0.5, h * 0.2, (255, 230, 150))
        star(x + w * 0.6, y + h * 0.38, h * 0.12, (200, 220, 255))
        star(x + w * 0.72, y + h * 0.66, h * 0.1, (255, 200, 160))
        for s in range(60):
            t = s / 60 * 6.28318
            ex = x + w * 0.5 + (w * 0.36) * _cos(t)
            ey = y + h * 0.52 + (h * 0.3) * _sin(t)
            rect(ex, ey, 1.6, 1.6, (150, 180, 255))
    elif kind == "dell":
        vgrad(x, y, w, h, (20, 60, 110), (40, 110, 170))
        for i in range(3):
            rect(x + w * (0.16 + i * 0.24), y + h * 0.3, w * 0.16, h * 0.5, (90, 150, 200))
            circle(x + w * (0.24 + i * 0.24), y + h * 0.42, 3, (120, 255, 170))
        line(x + w * 0.16, y + h * 0.78, x + w * 0.5, y + h * 0.5, GOLD, 3)
        line(x + w * 0.5, y + h * 0.5, x + w * 0.84, y + h * 0.2, GOLD, 3)
    elif kind == "nasdaq":
        vgrad(x, y, w, h, (240, 240, 245), (215, 220, 235))
        line(x + w * 0.1, y + h * 0.85, x + w * 0.92, y + h * 0.85, GREY, 2)
        line(x + w * 0.12, y + h * 0.25, x + w * 0.4, y + h * 0.4, RED, 3)
        line(x + w * 0.4, y + h * 0.4, x + w * 0.62, y + h * 0.32, RED, 3)
        line(x + w * 0.62, y + h * 0.32, x + w * 0.88, y + h * 0.72, RED, 3)
        tri(x + w * 0.88, y + h * 0.78, x + w * 0.8, y + h * 0.62, x + w * 0.92, y + h * 0.6, RED)
    elif kind == "punjab":
        vgrad(x, y, w, h, (250, 240, 210), (240, 215, 160))
        rect(x + w * 0.2, y + h * 0.24, 3, h * 0.56, INK)
        rect(x + w * 0.76, y + h * 0.24, 3, h * 0.56, INK)
        rect(x + w * 0.23, y + h * 0.26, w * 0.2, h * 0.16, (240, 130, 30))
        rect(x + w * 0.57, y + h * 0.26, w * 0.2, h * 0.16, (40, 90, 180))
        line(x + w * 0.43, y + h * 0.34, x + w * 0.57, y + h * 0.34, GREEN, 3)
        circle(x + w * 0.5, y + h * 0.62, h * 0.09, GREEN)
    elif kind == "madrid":
        vgrad(x, y, w, h, (40, 140, 80), (24, 100, 56))
        circle(x + w * 0.5, y + h * 0.5, h * 0.26, WHITE)
        circle(x + w * 0.5, y + h * 0.5, h * 0.09, INK)
        for dx, dy in ((-0.16, -0.12), (0.16, -0.12), (-0.16, 0.14), (0.16, 0.14)):
            circle(x + w * (0.5 + dx), y + h * (0.5 + dy), h * 0.05, INK)
        line(x + w * 0.08, y + h * 0.86, x + w * 0.92, y + h * 0.86, WHITE, 2)


LEADS = [
    (1, "cia", "CIA SYSTEM BREACHED", "ODNI HIT TOO", "AMERICAS", "CONFIRMED", "AP"),
    (2, "huawei", "HUAWEI GUILTY", "10 OF 12 COUNTS", "AMERICAS-ASIA", "CONFIRMED", "REUTERS"),
    (3, "migrants", "175 MIGRANTS MISSING", "BOAT FROM DAKAR LOST", "AFRICA", "CONFIRMED", "REUTERS"),
]

MEDIUM = [
    (4, "congo", "CONGO REBELS PULL BACK", "AFRICA", "CONFIRMED", "BBC/WHO"),
    (5, "copter", "TURKISH COPTER CRASH 5 DEAD", "EUROPE", "CONFIRMED", "REUTERS"),
    (6, "hostages", "CARTAGENA HOSTAGES FREE", "AMERICAS", "CONFIRMED", "AP"),
    (7, "putin", "PUTIN WARNS RETALIATION", "EUROPE", "REPORTED", "WIRE"),
    (8, "war", "LEAK: 720K WAR DEAD", "EUROPE", "REPORTED", "WIRE"),
    (9, "stars", "STAR SYSTEM SHOULD NOT EXIST", "SCIENCE", "CONFIRMED", "IAC"),
    (10, "dell", "DELL AI SALES DOUBLE", "AMERICAS", "CONFIRMED", "BARRON'S"),
    (11, "nasdaq", "NASDAQ FALLS 1.48%", "AMERICAS", "CONFIRMED", "REUTERS"),
    (12, "punjab", "PUNJAB ALLIANCE REUNITES", "ASIA", "CONFIRMED", "TIMES OF INDIA"),
    (13, "madrid", "REAL MADRID 5-1 PSV", "EUROPE", "CONFIRMED", "WIRE"),
]

PINS = {
    1: (0.20, 0.30), 2: (0.23, 0.34), 3: (0.44, 0.46), 4: (0.53, 0.58),
    5: (0.56, 0.34), 6: (0.24, 0.52), 7: (0.60, 0.26), 8: (0.58, 0.30),
    9: (0.10, 0.42), 10: (0.18, 0.38), 11: (0.22, 0.32), 12: (0.68, 0.42),
    13: (0.48, 0.34),
}

ALSO = [
    "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN T20",
    "TRUMP TEAM SPLIT OVER TARGETING IRAN LEADERS",
    "HOUTHI DRONE HITS RIYADH TOWER, 11 HURT",
    "THANKSGIVING CHAOS: O'HARE GROUND STOP",
    "MODI-MERZ DEEPEN INDIA-GERMANY TIES",
    "IRAN MEDICINE SHORTAGE BITES PATIENTS",
    "NATO EARLY-WARNING JETS FOR POLAND",
    "VENEZUELA PUBLIC DEBT $237.5 BILLION",
]

DATE_CHECK = [
    "SOORYAVANSHI 204 OFF 53 - 24 NOV, EXCLUDED",
    "NEPAL QUAKE 5.3 - 24 NOV, EXCLUDED",
    "LANDMINE MONITOR - 24 NOV, EXCLUDED",
]


def card_frame(x, y, w, h, accent):
    rect(x, y, w, h, WHITE)
    rect(x, y, w, 4, accent)
    rect(x, y + h - 2, w, 2, (200, 195, 180))


def badge(x, y, text, color):
    wdt = text_w(text, 1.1) + 8
    rect(x, y, wdt, 11, color)
    draw_text(x + 4, y + 2, text, 1.1, WHITE)
    return x + wdt


def render():
    # Masthead
    draw_text_c(W / 2, 14, "WEDNESDAY", 7.5, INK)
    draw_text_c(W / 2, 74, "25 NOVEMBER 2026", 5.2, RED)
    rect(24, 118, W - 48, 26, NAVY)
    draw_text_c(W / 2, 124, "35 STORIES · 15 MAP PINS · WORLD NEWS IN ONE IMAGE", 2.0, WHITE)

    # Leads
    lead_y, lead_h = 154, 208
    lead_w = (W - 48 - 16) / 3
    accents = (NAVY, RED, TEAL)
    for i, (num, kind, head, key, region, conf, src) in enumerate(LEADS):
        x = 24 + i * (lead_w + 8)
        card_frame(x, lead_y, lead_w, lead_h, accents[i])
        scene(kind, x + 6, lead_y + 10, lead_w - 12, 96)
        circle(x + 18, lead_y + 22, 11, RED)
        draw_text_c(x + 18, lead_y + 17, str(num), 1.5, WHITE)
        draw_wrap(x + 8, lead_y + 112, head, 2.1, INK, lead_w - 16)
        draw_text(x + 8, lead_y + 150, key, 2.6, accents[i])
        bx = badge(x + 8, lead_y + 178, conf, GREEN if conf == "CONFIRMED" else GOLD)
        draw_text(bx + 5, lead_y + 180, region + " · " + src, 1.15, GREY)

    # Map band
    map_y, map_h = 372, 150
    rect(24, map_y, W - 48, map_h, (196, 222, 240))
    rect(24, map_y, W - 48, 3, NAVY)
    draw_text(32, map_y + 8, "WORLD MAP - PINS MATCH STORY NUMBERS", 1.6, NAVY)
    mx, my, mw, mh = 40, map_y + 30, W - 80, map_h - 42
    ellipse(mx + mw * 0.17, my + mh * 0.36, mw * 0.11, mh * 0.3, SAND)
    ellipse(mx + mw * 0.26, my + mh * 0.72, mw * 0.06, mh * 0.26, SAND)
    ellipse(mx + mw * 0.52, my + mh * 0.3, mw * 0.07, mh * 0.22, SAND)
    ellipse(mx + mw * 0.53, my + mh * 0.62, mw * 0.08, mh * 0.3, SAND)
    ellipse(mx + mw * 0.72, my + mh * 0.34, mw * 0.16, mh * 0.28, SAND)
    ellipse(mx + mw * 0.84, my + mh * 0.74, mw * 0.06, mh * 0.16, SAND)
    for num, (fx, fy) in PINS.items():
        cx, cy = mx + mw * fx, my + mh * fy
        circle(cx, cy, 8.5, RED)
        draw_text_c(cx, cy - 4, str(num), 1.15, WHITE)

    # Medium grid 5 x 2
    med_y, med_h = 532, 118
    med_w = (W - 48 - 32) / 5
    for i, (num, kind, head, region, conf, src) in enumerate(MEDIUM):
        col, row = i % 5, i // 5
        x = 24 + col * (med_w + 8)
        y = med_y + row * (med_h + 8)
        card_frame(x, y, med_w, med_h, TEAL if i % 2 == 0 else GOLD)
        scene(kind, x + 5, y + 8, med_w - 10, 52)
        circle(x + 14, y + 18, 8.5, RED)
        draw_text_c(x + 14, y + 14, str(num), 1.15, WHITE)
        draw_wrap(x + 6, y + 64, head, 1.25, INK, med_w - 12)
        draw_text(x + 6, y + 102, region + " · " + src, 0.95, GREY)
        draw_text(x + 6, y + 110, conf, 0.95, GREEN if conf == "CONFIRMED" else (170, 120, 20))

    # Bottom panels
    bot_y = 786
    rect(24, bot_y, 600, 168, WHITE)
    rect(24, bot_y, 600, 4, NAVY)
    draw_text(32, bot_y + 10, "ALSO ON WEDNESDAY", 2.2, NAVY)
    for i, item in enumerate(ALSO):
        draw_text(32, bot_y + 36 + i * 15, "- " + item, 1.35, INK)
    rect(632, bot_y, W - 632 - 24, 168, (250, 240, 214))
    rect(632, bot_y, W - 632 - 24, 4, GOLD)
    draw_text(640, bot_y + 10, "DATE CHECK", 2.2, (150, 100, 16))
    draw_text(640, bot_y + 34, "NOT 25 NOV - EXCLUDED:", 1.3, INK)
    for i, item in enumerate(DATE_CHECK):
        draw_wrap(640, bot_y + 56 + i * 34, item, 1.25, INK, W - 632 - 40)
    rect(24, 962, W - 48, 34, INK)
    draw_text_c(W / 2, 970, "SOURCES: AP · REUTERS · BBC · WHO · IAC · BARRON'S · TIMES OF INDIA", 1.5, WHITE)


def downsample():
    out = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            acc0 = acc1 = acc2 = 0
            base = ((2 * y) * CW + 2 * x) * 3
            for dy in (0, 1):
                row = base + dy * CW * 3
                for dx in (0, 3):
                    i = row + dx
                    acc0 += canvas[i]
                    acc1 += canvas[i + 1]
                    acc2 += canvas[i + 2]
            o = (y * W + x) * 3
            out[o] = acc0 // 4
            out[o + 1] = acc1 // 4
            out[o + 2] = acc2 // 4
    return bytes(out)


def encode_png(rgb):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    render()
    png = encode_png(downsample())
    assert len(png) <= 1024 * 1024, "entry.png exceeds 1 MiB"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(png)


if __name__ == "__main__":
    main()
