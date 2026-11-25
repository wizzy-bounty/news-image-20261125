#!/usr/bin/env python3
"""news-image-20261125: sum up Wednesday 25 November 2026 in one image.

Pure stdlib. Draws a 1024x1024 broadsheet in code: giant masthead, UTC
timeline, 3 lead stories + 12 medium stories with flat pictograms, a
numbered world map, a 20-item ALSO list (35 stories total), a DATE CHECK
box of stories deliberately left out, and a sources footer.

Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). Runs twice,
byte-identical: no time, no randomness, no network, no files read.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ----
PAPER = (252, 246, 230)
PANEL = (255, 253, 247)
INK = (24, 30, 54)
RED = (178, 34, 34)
DARKRED = (122, 22, 30)
GREEN = (24, 104, 62)
AMBER = (168, 112, 16)
TEAL = (14, 92, 108)
NAVY = (22, 44, 84)
GOLD = (176, 141, 60)
GREY = (96, 96, 96)
DARKGREY = (58, 58, 58)
SLATE = (122, 140, 160)
WHITE = (255, 255, 255)
CREAM2 = (238, 228, 204)

# ---- 5x7 bitmap font, drawn from scratch ----
# Each glyph: 7 rows, each a 5-bit int (bit 4 = leftmost pixel).
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
}
# Characters outside the font map to these before rendering.
NORMALIZE = {
    '\u2013': '-', '\u2014': '-', '\u2019': "'", '\u2018': "'",
    '\u201c': '"', '\u201d': '"', '\u02bb': "'", '\u014d': 'O',
    '\u00e9': 'E', '\u00e8': 'E', '\u00fc': 'U', '\u00e4': 'A',
    '\u00f6': 'O', '\u00df': 'S', '\u00b7': '.', '\u00d7': 'X',
    '\u2212': '-', '\u2011': '-', '\u00a0': ' ',
}
ADV = 6  # advance per char at scale 1


def clean(s):
    out = []
    for ch in s:
        if ch in NORMALIZE:
            out.append(NORMALIZE[ch])
        elif ch in FONT:
            out.append(ch)
        elif 'a' <= ch <= 'z':
            out.append(ch.upper())
        else:
            out.append(' ')
    return ''.join(out)


def text_w(s, scale):
    return len(clean(s)) * ADV * scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def border(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill(cx - dx, yy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((yy - cy) / ry) ** 2 if ry else 0
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.fill(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for a in range(0, 360, 2):
                import math
                x = int(cx + rr * math.cos(math.radians(a)))
                y = int(cy + rr * math.sin(math.radians(a)))
                self.set(x, y, c)

    def text(self, x, y, s, scale, c, bold=False):
        s = clean(s)
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill(cx + col * scale, y + row * scale, scale, scale, c)
                        if bold:
                            self.fill(cx + col * scale + 1, y + row * scale, scale, scale, c)
            cx += ADV * scale

    def text_c(self, cx, y, s, scale, c, bold=False):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, c, bold)

    def text_r(self, x, y, s, scale, c, bold=False):
        self.text(x - text_w(s, scale), y, s, scale, c, bold)


def wrap(s, width, scale):
    """Greedy word wrap; returns list of lines fitting width px."""
    s = clean(s)
    words, lines, cur = s.split(' '), [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def trunc(s, width, scale):
    s = clean(s)
    while s and text_w(s, scale) > width:
        s = s[:-1]
    return s


def png_bytes(c):
    def chunk(kind, data):
        out = kind + data
        return struct.pack('>I', len(data)) + out + struct.pack('>I', zlib.crc32(out) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', c.w, c.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)
        raw += c.px[yy * c.w * 3:(yy + 1) * c.w * 3]
    idat = zlib.compress(bytes(raw), 6)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', idat) + chunk(b'IEND', b''))


# ---- flat pictograms: simple silhouettes, 2-4 colours each ----
# Every pictogram draws inside (x, y, w, h) on its coloured band.

def pic_monitor(c, x, y, w, h):
    # CIA breach: monitor, red padlock, warning bars
    c.fill(x + w // 2 - 34, y + 8, 68, 40, (210, 220, 235))
    c.fill(x + w // 2 - 30, y + 12, 60, 32, (18, 34, 64))
    c.fill(x + w // 2 - 14, y + 48, 28, 4, (210, 220, 235))
    c.fill(x + w // 2 - 22, y + 52, 44, 3, (210, 220, 235))
    for i, yy in enumerate((y + 16, y + 24, y + 32)):
        c.fill(x + w // 2 - 24, yy, 26, 3, (90, 200, 120) if i != 1 else (240, 200, 60))
    c.fill(x + w - 52, y + 6, 26, 22, (200, 40, 40))
    c.fill(x + w - 48, y + 14, 18, 4, (255, 255, 255))
    c.fill(x + w - 41, y + 18, 4, 6, (255, 255, 255))


def pic_court(c, x, y, w, h):
    # Huawei verdict: courthouse columns + gavel
    c.fill(x + w // 2 - 40, y + 10, 80, 6, (232, 214, 160))
    for i in range(4):
        c.fill(x + w // 2 - 36 + i * 20, y + 16, 8, 26, (232, 214, 160))
    c.fill(x + w // 2 - 44, y + 42, 88, 5, (232, 214, 160))
    c.fill(x + w - 46, y + 8, 34, 5, (240, 200, 60))
    c.fill(x + w - 38, y + 13, 5, 12, (240, 200, 60))
    c.fill(x + w - 48, y + 26, 38, 4, (240, 200, 60))


def pic_boat(c, x, y, w, h):
    # Migrants at sea: wooden pirogue + waves
    c.fill(x + 8, y + h - 26, w - 16, 4, (120, 200, 230))
    c.fill(x + 20, y + h - 18, w - 40, 4, (90, 180, 215))
    c.fill(x + 34, y + h - 10, w - 68, 4, (120, 200, 230))
    bx, by = x + w // 2 - 52, y + h - 52
    c.fill(bx, by, 104, 12, (146, 96, 52))
    c.fill(bx + 8, by + 12, 88, 6, (120, 76, 40))
    c.fill(bx + 50, by - 22, 4, 24, (120, 76, 40))
    c.fill(bx + 54, by - 20, 30, 16, (240, 232, 200))
    for i in range(3):
        c.disc(bx + 22 + i * 26, by - 6, 5, (24, 30, 54))


def pic_tent(c, x, y, w, h):
    # DR Congo: medical tent + red cross
    tx, ty = x + w // 2 - 40, y + h - 26
    c.fill(tx, ty, 80, 22, (236, 228, 200))
    c.fill(tx + 4, ty - 10, 72, 10, (200, 60, 50))
    c.fill(tx + 34, ty - 16, 12, 6, (200, 60, 50))
    c.fill(x + w - 40, y + 6, 26, 26, WHITE)
    c.fill(x + w - 32, y + 10, 10, 18, (200, 40, 40))
    c.fill(x + w - 36, y + 14, 18, 10, (200, 40, 40))


def pic_heli(c, x, y, w, h):
    # Helicopter crash: tilted heli + smoke
    c.fill(x + 14, y + 6, w - 28, 3, (200, 200, 200))
    hx, hy = x + w // 2 - 40, y + 12
    c.ellipse(hx + 28, hy + 8, 26, 9, (220, 220, 220))
    c.fill(hx + 48, hy + 6, 30, 5, (220, 220, 220))
    c.fill(hx + 74, hy + 1, 4, 12, (220, 220, 220))
    c.fill(hx + 6, hy + 2, 18, 8, (150, 200, 240))
    c.fill(hx + 4, hy + 20, 14, 3, (160, 160, 160))
    c.fill(hx + 40, hy + 20, 14, 3, (160, 160, 160))
    c.disc(x + w - 26, y + h - 12, 6, (240, 160, 60))
    c.disc(x + w - 38, y + h - 9, 4, (240, 190, 90))


def pic_shop(c, x, y, w, h):
    # Supermarket standoff: awning storefront
    c.fill(x + 10, y + 6, w - 20, 10, (200, 40, 40))
    for i in range(6):
        c.fill(x + 12 + i * ((w - 24) // 6), y + 6, (w - 24) // 12, 10, WHITE)
    c.fill(x + 16, y + 18, w - 32, h - 26, (236, 228, 200))
    c.fill(x + w // 2 - 20, y + 22, 40, h - 30, (90, 140, 190))
    c.fill(x + w // 2 - 2, y + 22, 4, h - 30, (236, 228, 200))
    c.fill(x + 22, y + 24, 24, 12, (240, 200, 60))
    c.fill(x + w - 46, y + 24, 24, 12, (240, 200, 60))


def pic_derrick(c, x, y, w, h):
    # Oil war: derrick + flame
    dx = x + w // 2
    base = y + h - 6
    c.line(dx - 20, base, dx + 4, y + 8, (240, 200, 60))
    c.line(dx + 20, base, dx - 2, y + 8, (240, 200, 60))
    c.line(dx - 13, y + 22, dx + 13, y + 22, (240, 200, 60))
    c.line(dx - 7, y + 32, dx + 9, y + 32, (240, 200, 60))
    c.fill(dx - 24, base, 48, 3, (240, 200, 60))
    c.disc(x + w - 30, y + 12, 8, (240, 120, 40))
    c.disc(x + w - 30, y + 15, 5, (250, 200, 60))


def pic_graves(c, x, y, w, h):
    # War dead: row of crosses + rising bars
    for i in range(5):
        gx = x + 16 + i * 18
        gy = y + h - 30 - (i % 2) * 6
        c.fill(gx, gy, 4, 16, (220, 220, 220))
        c.fill(gx - 4, gy + 3, 12, 4, (220, 220, 220))
    for i, bh in enumerate((10, 16, 24, 32)):
        c.fill(x + w - 58 + i * 13, y + h - 12 - bh, 9, bh, (200, 80, 60))


def pic_stars(c, x, y, w, h):
    # Triple star: three glowing stars
    def star(sx, sy, r, col):
        c.disc(sx, sy, r, col)
        c.fill(sx - 1, sy - r - 6, 3, 2 * r + 12, col)
        c.fill(sx - r - 6, sy - 1, 2 * r + 12, 3, col)
    star(x + w // 2 - 34, y + h // 2 - 4, 7, (255, 240, 180))
    star(x + w // 2 + 6, y + h // 2 + 6, 5, (255, 255, 255))
    star(x + w // 2 + 38, y + h // 2 - 10, 9, (255, 210, 120))
    for sx, sy in ((x + 16, y + 10), (x + w - 18, y + h - 14), (x + 30, y + h - 12)):
        c.disc(sx, sy, 2, WHITE)


def pic_laptop(c, x, y, w, h):
    # Dell: laptop + rising chart arrow
    lx, ly = x + w // 2 - 52, y + h - 44
    c.fill(lx, ly, 76, 26, (30, 40, 60))
    c.fill(lx + 4, ly + 4, 68, 18, (90, 200, 140))
    c.fill(lx - 8, ly + 26, 92, 4, (200, 200, 200))
    c.line(x + w - 52, y + h - 12, x + w - 40, y + 16, (90, 200, 140))
    c.line(x + w - 40, y + 16, x + w - 28, y + 26, (90, 200, 140))
    c.line(x + w - 28, y + 26, x + w - 16, y + 8, (90, 200, 140))
    c.line(x + w - 16, y + 8, x + w - 22, y + 8, (90, 200, 140))
    c.line(x + w - 16, y + 8, x + w - 16, y + 14, (90, 200, 140))


def pic_chartdown(c, x, y, w, h):
    # Nasdaq fall: red plunging line + bars
    for i, bh in enumerate((26, 20, 14, 8)):
        c.fill(x + 14 + i * 14, y + h - 12 - bh, 10, bh, (200, 200, 200))
    c.line(x + 12, y + 12, x + 34, y + 22, (240, 70, 60))
    c.line(x + 34, y + 22, x + 58, y + 20, (240, 70, 60))
    c.line(x + 58, y + 20, x + w - 16, y + h - 14, (240, 70, 60))
    c.disc(x + w - 16, y + h - 14, 4, (240, 70, 60))


def pic_ballot(c, x, y, w, h):
    # Punjab alliance: ballot box + big tick
    bx, by = x + w // 2 - 30, y + h - 40
    c.fill(bx, by, 60, 28, (240, 160, 50))
    c.fill(bx - 4, by - 6, 68, 6, (200, 120, 30))
    c.fill(bx + 24, by - 12, 12, 6, (24, 30, 54))
    c.fill(bx + 8, by + 8, 44, 12, WHITE)
    c.line(bx + 12, by + 14, bx + 20, by + 20, (24, 104, 62))
    c.line(bx + 20, by + 20, bx + 40, by + 2, (24, 104, 62))
    c.line(x + w - 44, y + 10, x + w - 30, y + 24, (240, 160, 50))
    c.line(x + w - 30, y + 24, x + w - 14, y + 6, (240, 160, 50))


def pic_football(c, x, y, w, h):
    # Real Madrid 5-1: goal + ball
    gx, gy = x + 12, y + 8
    c.fill(gx, gy, 4, h - 26, WHITE)
    c.fill(gx + w - 96, gy, 4, h - 26, WHITE)
    c.fill(gx, gy, w - 92, 4, WHITE)
    for i in range(5):
        c.vline(gx + 14 + i * 16, gy + 4, h - 30, (220, 220, 220))
    c.hline(gx + 4, gy + 12, w - 100, (220, 220, 220))
    c.disc(x + w - 34, y + h - 22, 12, WHITE)
    c.disc(x + w - 34, y + h - 22, 5, (24, 30, 54))
    c.fill(x + w - 46, y + h - 34, 24, 3, (24, 30, 54))


def pic_cricket(c, x, y, w, h):
    # England v Australia: bat, ball, stumps
    for i in range(3):
        c.fill(x + 16 + i * 8, y + 12, 4, 26, (240, 200, 120))
    c.fill(x + 14, y + 10, 30, 4, (240, 200, 120))
    c.line(x + w - 56, y + 10, x + w - 30, y + h - 16, (220, 190, 140))
    c.fill(x + w - 62, y + 6, 14, 10, (220, 190, 140))
    c.disc(x + w - 24, y + 16, 7, (200, 40, 40))
    c.fill(x + w // 2 - 30, y + h - 12, 60, 3, (24, 104, 62))


def pic_split(c, x, y, w, h):
    # Iran split: two opposing arrows + ship
    c.line(x + 14, y + 14, x + w // 2 - 6, y + 14, (240, 200, 60))
    c.line(x + w // 2 - 6, y + 14, x + w // 2 - 14, y + 8, (240, 200, 60))
    c.line(x + w // 2 - 6, y + 14, x + w // 2 - 14, y + 20, (240, 200, 60))
    c.line(x + w // 2 + 6, y + h - 20, x + w - 14, y + h - 20, (120, 200, 230))
    c.line(x + w // 2 + 6, y + h - 20, x + w // 2 + 14, y + h - 26, (120, 200, 230))
    c.line(x + w // 2 + 6, y + h - 20, x + w // 2 + 14, y + h - 14, (120, 200, 230))
    c.fill(x + w // 2 - 34, y + h - 38, 68, 10, (200, 200, 200))
    c.fill(x + w // 2 - 20, y + h - 50, 40, 12, (160, 160, 160))

PICS = {
    'monitor': pic_monitor, 'court': pic_court, 'boat': pic_boat,
    'tent': pic_tent, 'heli': pic_heli, 'shop': pic_shop,
    'derrick': pic_derrick, 'graves': pic_graves, 'stars': pic_stars,
    'laptop': pic_laptop, 'chartdown': pic_chartdown, 'ballot': pic_ballot,
    'football': pic_football, 'cricket': pic_cricket, 'split': pic_split,
}

# ---- stories: (num, region, badge, headline, sub, source, key, band, pic) ----
LEADS = [
    (1, 'AMERICAS', 'CONFIRMED', "CIA'S UNCLASSIFIED SPY SYSTEM BREACHED",
     "Open-source intel system hit in a cyberattack; no classified data involved, issue resolved. ODNI also hit.",
     'AP - NYT - Reuters', 'CIA BREACH', NAVY, 'monitor'),
    (2, 'AMERICAS / ASIA', 'CONFIRMED', 'HUAWEI GUILTY ON 10 OF 12 COUNTS',
     "Brooklyn jury convicts on bank fraud and trade-secret theft over Iran business; acquits on racketeering.",
     'Reuters - AP - FT', '10 OF 12', DARKRED, 'court'),
    (3, 'AFRICA', 'CONFIRMED', '175 MIGRANTS MISSING AS BOAT VANISHES',
     "Contact lost with a Europe-bound pirogue from Dakar's Yoff; mayor puts 175 aboard. Navy rescued 974 Monday.",
     'Reuters - Yoff mayor', '175 MISSING', TEAL, 'boat'),
]
MEDIUM = [
    (4, 'AFRICA', 'CONFIRMED', 'CONGO REBELS CALL OFF BUNIA ADVANCE',
     "CRP pulls back amid Uganda talks; WHO evacuates Ebola teams from Akwe.",
     'BBC - WHO', 'REBELS HALT', (58, 84, 48), 'tent'),
    (5, 'EUROPE', 'CONFIRMED', 'TURKISH HELICOPTER CRASH KILLS FIVE',
     'Cougar falls near Eskisehir in training; 2nd fatal crash in 12 days.',
     'Reuters - Al Jazeera', '5 KILLED', (74, 74, 88), 'heli'),
    (6, 'AMERICAS', 'CONFIRMED', 'HOSTAGES FREED IN CARTAGENA STANDOFF',
     'Gunmen fleeing a failed robbery held about 25 in a supermarket; all freed.',
     'AP - Starlit Daily', '25 HELD', (120, 72, 32), 'shop'),
    (7, 'EUROPE', 'REPORTED', "PUTIN: RETALIATION 'INEVITABLE'",
     'Warning as Ukraine keeps hitting Russian oil plants; war escalates.',
     'WireMinute', 'OIL WAR', (40, 40, 44), 'derrick'),
    (8, 'EUROPE', 'REPORTED', 'LEAKED RECORDS: 720,000 WAR DEAD',
     'Leaked records put war dead far above official figures; 1,000+ suicides.',
     'WireMinute', '720,000', (88, 30, 34), 'graves'),
    (9, 'SCIENCE', 'CONFIRMED', 'STAR SYSTEM THAT SHOULD NOT EXIST',
     'Welopoai, 28 ly away: closest triple star with two white dwarfs.',
     'IAC - SciTechDaily', '28 LY', (20, 20, 52), 'stars'),
    (10, 'AMERICAS', 'CONFIRMED', "DELL BEATS ON AI; $25BN BUYBACK",
     'AI-server sales more than double; backlog vetted for quality, capital.',
     "Barron's - AI Circle", '$25BN', (16, 74, 96), 'laptop'),
    (11, 'AMERICAS', 'CONFIRMED', 'NASDAQ DROPS 1.48% AS NVIDIA SLIDES',
     'Nasdaq down 356 to 23,733; Nvidia -5.86% a day after its 31.5% surge.',
     'Reuters - Barron\'s', '-1.48%', (96, 26, 60), 'chartdown'),
    (12, 'ASIA', 'CONFIRMED', 'BJP AND AKALI DAL REUNITE FOR PUNJAB',
     'Alliance for 2027 Punjab polls ends a six-year split; SAD rejoins the NDA.',
     'Times of India', '2027 POLLS', (128, 84, 16), 'ballot'),
    (13, 'EUROPE', 'CONFIRMED', 'REAL MADRID HIT PSV 5-1',
     'Bellingham stunner and Mbappe brace; Madrid top of the table.',
     'Starlit Daily', '5-1', (20, 72, 44), 'football'),
    (14, 'EUROPE', 'CONFIRMED', 'ENGLAND BEAT AUSTRALIA',
     'Chasing 185 to level the series; Fraser-McGurk hits 27 off 13.',
     'Jagran Josh', '8 WICKETS', (30, 88, 52), 'cricket'),
    (15, 'MIDEAST', 'REPORTED', 'TRUMP TEAM SPLIT ON TARGETING IRAN',
     'Officials split as US blockade enters day 130; Tehran sets seven terms.',
     'WireMinute', 'DAY 130', (92, 56, 30), 'split'),
]
ALSO = [
    (16, 'Houthi drone hits Riyadh tower, 2nd time in a week; 11 injured.'),
    (17, 'Israel says Iran is developing chemical weapons, plotting to kill Trump.'),
    (18, 'Mosque loudspeaker seizures in Israel draw "religious war" charge.'),
    (19, '92-year-old Nigerian emir suspended after sexual assault allegation.'),
    (20, 'US Army to detonate 4+ tonnes of lead azide in Iowa; residents urged to leave.'),
    (21, "Libya's Haftar visits Turkiye days after Ukraine hit a Russian warship."),
    (22, 'Lukashenko offers to fly with Zelensky to Moscow for Putin talks.'),
    (23, 'US House counsel denies backing controversial raid on Ilhan Omar\'s home.'),
    (24, 'Blurry video of suspected lion triggers major search in Istanbul.'),
    (25, "Thanksgiving travel chaos: O'Hare airport hits a ground stop."),
    (26, "Modi holds talks with Germany's Merz on strategic partnership."),
    (27, 'Iran medicine shortage: patients hunt for drugs as pharmacies shut.'),
    (28, 'Great Barrier Reef holds wider coral diversity; 12 species "resurrected".'),
    (29, 'Spacecraft films asteroid-on-asteroid solar eclipse at Didymos.'),
    (30, 'Ben Stokes registers for IPL 2027 auction; 12 Bangladesh players listed.'),
    (31, 'NATO to deploy early-warning aircraft in Poland after missile reports.'),
    (32, 'Houthis report deaths and missing after Saudi strikes in SW Yemen.'),
    (33, 'New cinematic Ramayana ignites debate in India.'),
    (34, 'US targets chip smuggling to China after Huang\'s Nvidia return.'),
    (35, 'Venezuela officially reports total public debt of $237.5 billion.'),
]
DATECHECK = [
    'Sooryavanshi 204 off 53 balls - 24 Nov (List A record)',
    'Gukesh-Sindarov Game 1 draw - 24 Nov (Game 2 is today)',
    'Landmine Monitor 2026: 6,929 casualties - 24 Nov',
    'Nepal earthquake M5.3 - 24 Nov',
    'CAS reinstates Senegal as AFCON champions - 24 Nov',
    'Indonesia VP Gibran resigned - 12 Nov (not 25 Nov)',
]


# ---- layout ----

def badge_color(badge):
    return GREEN if badge == 'CONFIRMED' else AMBER


def draw_story(c, x, y, w, h, story, lead=False):
    num, region, badge, head, sub, src, key, band, pic = story
    pic_h = 88 if lead else 46
    c.fill(x, y, w, h, PANEL)
    c.border(x, y, w, h, INK, 2)
    # pictogram band + key number on a solid dark tab inside it
    c.fill(x + 2, y + 2, w - 4, pic_h, band)
    PICS[pic](c, x + 2, y + 2, w - 4, pic_h)
    ks = 3 if lead else 2
    kw = text_w(key, ks)
    tab_h = 7 * ks + 6  # key-tab height: glyph rows plus padding
    ty = y + 2 + pic_h - tab_h - 2
    c.fill(x + 4, ty - 3, kw + 14, tab_h, INK)
    c.text(x + 11, ty, key, ks, WHITE, bold=True)
    # meta row: number, region, badge
    my = y + pic_h + 5
    c.text(x + 8, my, 'No.%d' % num, 1, INK, bold=True)
    c.text(x + 8 + text_w('No.%d  ' % num, 1), my, region, 1, GREY, bold=True)
    bw = text_w(badge, 1) + 10
    c.fill(x + w - 8 - bw, my - 2, bw, 11, badge_color(badge))
    c.text(x + w - 8 - bw + 5, my, badge, 1, WHITE, bold=True)
    # headline, 2 lines
    hy = my + 12
    hl = wrap(head, w - 16, 2)[:2]
    for i, ln in enumerate(hl):
        c.text(x + 8, hy + i * 15, ln, 2, INK, bold=True)
    # sub
    sy = hy + 32
    sl = wrap(sub, w - 16, 1)[:3 if lead else 2]
    for i, ln in enumerate(sl):
        c.text(x + 8, sy + i * 9, ln, 1, DARKGREY)
    # source line
    c.text(x + 8, y + h - 11, '- ' + src, 1, GREY)


# world map: dot continents (defined in the 600x92 map space) + numbered pins
CONTINENTS = [
    (95, 22, 78, 20), (205, 8, 16, 6), (155, 60, 26, 22),
    (315, 20, 32, 13), (325, 48, 34, 24), (445, 23, 95, 22),
    (500, 56, 28, 8), (530, 68, 30, 11),
]
PINS = [  # (story num, lon, lat, dx, dy) dx/dy nudge the label off a cluster
    (1, -77, 39, 0, 0), (2, -74, 40.6, 20, 14), (3, -17.4, 14.7, 0, 0),
    (4, 30.2, 1.5, 0, 0), (5, 30.5, 39.8, 14, 10), (6, -75.5, 10.4, 0, 0),
    (7, 37.6, 55.7, 0, 0), (8, 30.5, 50.4, -16, 14), (9, -155.5, 19.8, 0, 0),
    (10, -97.7, 30.5, 0, 0), (11, -74, 40.7, -20, -14), (12, 75.8, 30.9, 0, 0),
    (13, -3.7, 40.4, 0, 0), (14, -1.5, 52, 10, -10), (15, 51.4, 35.7, 0, 0),
]


def draw_map(c, x, y, w, h):
    c.fill(x, y, w, h, PANEL)
    c.border(x, y, w, h, INK, 2)
    c.text(x + 8, y + 5, 'WHERE IT HAPPENED - pins match story numbers', 1, INK, bold=True)
    mx, my, mw, mh = x + 8, y + 18, w - 16, h - 24
    for gy in range(my, my + mh, 6):
        for gx in range(mx, mx + mw, 6):
            px, py = gx - mx, gy - my
            inside = False
            for (ccx, ccy, rx, ry) in CONTINENTS:
                sx, sy = (px - ccx) / rx, (py - ccy) / ry
                if sx * sx + sy * sy <= 1.0:
                    inside = True
                    break
            if inside:
                c.fill(gx, gy, 3, 3, SLATE)
    for (num, lon, lat, dx, dy) in PINS:
        px = mx + int((lon + 180) / 360 * mw)
        py = my + int((90 - lat) / 180 * mh)
        lx, ly = px + dx, py + dy
        if dx or dy:
            c.line(px, py, lx, ly, RED)
        c.disc(lx, ly, 7, RED)
        c.ring(lx, ly, 7, WHITE, 1)
        s = str(num)
        c.text(lx - text_w(s, 1) // 2, ly - 3, s, 1, WHITE, bold=True)


def draw_datecheck(c, x, y, w, h):
    c.fill(x, y, w, h, PANEL)
    c.border(x, y, w, h, RED, 2)
    c.text(x + 8, y + 5, 'DATE CHECK - LEFT OUT (OTHER DAYS)', 1, RED, bold=True)
    for i, item in enumerate(DATECHECK):
        iy = y + 22 + i * 15
        c.text(x + 8, iy, 'x', 1, RED, bold=True)
        c.text(x + 20, iy, trunc(item, w - 28, 1), 1, DARKGREY)


def draw_also(c, x, y, w):
    c.text(x, y, 'ALSO ON WEDNESDAY 25 NOVEMBER', 1, INK, bold=True)
    c.hline(x, y + 11, w, INK, 2)
    colw = (w - 20) // 2
    for i, (num, item) in enumerate(ALSO):
        col = 0 if i < 10 else 1
        row = i % 10
        ix = x + col * (colw + 20)
        iy = y + 17 + row * 12
        c.text(ix, iy, str(num), 1, RED, bold=True)
        c.text(ix + 22, iy, trunc(item, colw - 22, 1), 1, DARKGREY)


def build():
    c = Canvas(W, H, PAPER)
    # kicker + masthead
    c.text_c(W // 2, 6, 'THE WORLD IN ONE PICTURE - MAKE.FUN DAILY', 1, RED, bold=True)
    c.text_c(W // 2, 20, 'WEDNESDAY 25 NOVEMBER 2026', 5, INK, bold=True)
    c.hline(14, 60, W - 28, INK, 2)
    c.hline(14, 63, W - 28, INK, 1)
    c.text_c(W // 2, 68, '35 STORIES - 6 REGIONS + SPACE - 15 PICTURED - EVERY STORY FROM THIS ONE DAY',
             1, INK, bold=True)
    c.hline(14, 84, W - 28, INK, 1)
    # timeline strip
    c.fill(14, 88, W - 28, 20, NAVY)
    c.text(22, 93, 'THE DAY IN UTC', 1, (255, 210, 90), bold=True)
    c.text(22 + text_w('THE DAY IN UTC  ', 1), 93,
           '20:33 (24 NOV) CIA breach reported by AP - 00:23 Congo rebels pull back - 00:45 Turkish crash, 5 killed - 01:35 cut-off',
           1, WHITE)
    # leads
    lw = (W - 28 - 16) // 3
    for i, st in enumerate(LEADS):
        draw_story(c, 14 + i * (lw + 8), 114, lw, 192, st, lead=True)
    # medium grid 4 x 3
    mw = (W - 28 - 24) // 4
    for i, st in enumerate(MEDIUM):
        r, col = divmod(i, 4)
        draw_story(c, 14 + col * (mw + 8), 312 + r * 136, mw, 130, st)
    # map + date check
    draw_map(c, 14, 716, 612, 116)
    draw_datecheck(c, 634, 716, W - 14 - 634, 116)
    # also list
    draw_also(c, 14, 838, W - 28)
    # footer
    c.hline(14, 978, W - 28, INK, 2)
    srcs = ('Sources: AP - Reuters - BBC - Al Jazeera - NYT - FT - The Hindu BusinessLine - Times of India - '
            'Jagran Josh - Barron\'s - IAC - WHO - Turkish Defence Ministry - Starlit Daily - WireMinute - '
            'Stockbiz - Cyprus Inform - Huddleworld - Disclosure News - LifeBitmaps - Cricbuzz - DW')
    for i, ln in enumerate(wrap(srcs, W - 28, 1)):
        c.text(14, 984 + i * 9, ln, 1, GREY)
    c.text(14, 1004, 'BADGES: CONFIRMED = 2+ outlets - OFFICIAL = on-the-record statement - REPORTED = 1 outlet / single source',
           1, GREY)
    c.text(14, 1013, 'All stories first reported 25 Nov in at least one timezone; most first published late 24 Nov UTC.',
           1, GREY)
    c.text_r(W - 14, 1013, 'Original drawings, drawn in code - @quick-raven-30', 1, INK, bold=True)
    return c


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(outdir, 'entry.png'), 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
