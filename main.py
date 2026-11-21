#!/usr/bin/env python3
"""THE GLOBAL FRONT PAGE -- Saturday 21 November 2026.

A deterministic program that draws a one-page newspaper front page
summing up the world's news of Saturday 21 November 2026 and writes it
to /output/entry.png (1024x1024, PNG, <= 1 MiB).

Every story, date and figure below was checked against live reporting
on 21 November 2026 (Reuters, AP, Al Jazeera, Arab News, ESA, FIA, IMD,
ISW and others); see SOURCES.md for the source of each fact. No network
access, no clock, no randomness: the same run always writes the same bytes.

Run:  python3 main.py            (writes /output/entry.png)
      OUTPUT_DIR=out python3 main.py   (writes out/entry.png, for local tests)
Requires: Python 3 standard library ONLY. The type is a bitmap font
hand-drawn in this file (a 5x7 grid per glyph, scaled up where the page
needs it), the PNG is encoded by hand with zlib, and all drawing is done
on a plain bytearray canvas.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024
OUT = os.path.join(
    os.environ.get("OUTPUT_DIR")
    or os.environ.get("MAKEFUN_OUTPUT_DIR")
    or "/output",
    "entry.png",
)

# ---------------------------------------------------------------- palette
PAPER = (248, 244, 235)
INK = (24, 24, 24)
INK_SOFT = (78, 76, 70)
RULE = (24, 24, 24)
RED = (176, 30, 42)
RED_DARK = (124, 18, 28)
BLUE = (28, 74, 118)
TEAL = (12, 102, 102)
GOLD = (150, 106, 14)
CREAM = (255, 252, 245)
GREY_BG = (233, 229, 219)
GREY_LINE = (188, 182, 168)
MAP_LAND = (204, 212, 198)
MAP_SEA = (224, 233, 238)
WHITE = (255, 255, 255)
NIGHT = (18, 26, 44)
SPACE = (10, 12, 26)

# ---------------------------------------------------------------- hand font
# One bitmap font, drawn by hand on a 5-wide, 7-tall grid. Each glyph is
# (advance, row0, ..., row6): advance is the glyph's width in grid units
# including its trailing gap, and each row is five characters, '1' for a
# filled cell, '0' for empty, left column first. Capitals and digits use
# all seven rows; lowercase letters sit on rows 2..6 with descenders on
# row 6, so every glyph shares the same baseline. The renderer scales
# the grid by an integer factor (1, 2, 3 or 7) and can double-strike a
# glyph one pixel to the right for a bold weight.
GLYPHS = {
    32: (3, "00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    33: (3, "00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    34: (4, "01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    35: (6, "01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    36: (6, "00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    37: (6, "11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    38: (6, "01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    39: (3, "00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    40: (4, "00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    41: (4, "01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    42: (6, "00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    43: (6, "00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    44: (3, "00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    45: (5, "00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    46: (3, "00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    47: (5, "00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    48: (6, "01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    49: (4, "00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    50: (6, "01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    51: (6, "11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    52: (6, "00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    53: (6, "11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    54: (6, "00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    55: (6, "11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    56: (6, "01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    57: (6, "01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    58: (3, "00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    59: (3, "00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    60: (5, "00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    61: (6, "00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    62: (5, "01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    63: (6, "01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    64: (6, "01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    65: (6, "01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    66: (6, "11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    67: (6, "01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    68: (6, "11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    69: (6, "11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    70: (6, "11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    71: (6, "01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    72: (6, "10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    73: (4, "01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    74: (5, "00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    75: (6, "10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    76: (5, "10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    77: (6, "10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    78: (6, "10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    79: (6, "01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    80: (6, "11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    81: (6, "01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    82: (6, "11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    83: (6, "01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    84: (6, "11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    85: (6, "10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    86: (6, "10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    87: (6, "10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    88: (6, "10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    89: (6, "10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    90: (6, "11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    91: (4, "01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    92: (5, "10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    93: (4, "01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    94: (6, "00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    95: (6, "00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    96: (3, "00100", "00100", "00010", "00000", "00000", "00000", "00000"),
    97: (6, "00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    98: (6, "10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    99: (6, "00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    100: (6, "00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    101: (6, "00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    102: (5, "00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    103: (6, "00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    104: (6, "10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    105: (4, "00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    106: (4, "00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    107: (5, "10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    108: (4, "01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    109: (6, "00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    110: (6, "00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    111: (6, "00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    112: (6, "00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    113: (6, "00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    114: (5, "00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    115: (6, "00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    116: (5, "01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    117: (6, "00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    118: (6, "00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    119: (6, "00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    120: (6, "00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    121: (6, "00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    122: (6, "00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    123: (4, "00010", "00100", "00100", "01100", "00100", "00100", "00010"),
    124: (3, "00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    125: (4, "01000", "00100", "00100", "00110", "00100", "00100", "01000"),
    126: (6, "00000", "00000", "01101", "10110", "00000", "00000", "00000"),
    # extras used by the page: pound, middle dot, accented vowels,
    # en/em dashes, curly quotes, minus sign, small square bullet
    163: (6, "00110", "01000", "01000", "11110", "01000", "01000", "11111"),
    183: (3, "00000", "00000", "01100", "01100", "00000", "00000", "00000"),
    233: (6, "00010", "00100", "01110", "10001", "11111", "10000", "01110"),
    237: (4, "00010", "00100", "00000", "01100", "00100", "00100", "01110"),
    252: (6, "01010", "00000", "10001", "10001", "10001", "10011", "01101"),
    8211: (5, "00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    8212: (6, "00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    8216: (3, "00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    8217: (3, "00100", "00100", "00010", "00000", "00000", "00000", "00000"),
    8220: (4, "01010", "01010", "00100", "00000", "00000", "00000", "00000"),
    8221: (4, "01010", "01010", "01000", "00000", "00000", "00000", "00000"),
    8722: (6, "00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    9642: (5, "00000", "00000", "01110", "01110", "01110", "00000", "00000"),
}
_MISSING = GLYPHS[63]  # unknown characters fall back to '?'


def text_w(s, sc):
    """Width in pixels of string s drawn at integer scale sc."""
    total = 0
    for ch in s:
        total += GLYPHS.get(ord(ch), _MISSING)[0]
    return total * sc - sc if total else 0


def _blit_glyph(cv, gx, gy, rows, sc, color):
    """Paint one glyph whose top-left grid cell is (gx, gy); each set
    cell becomes an sc x sc block of `color` on the canvas buffer."""
    buf = cv.px
    stride = cv.pitch
    r, g, b = color
    for row in range(7):
        line = rows[row + 1]
        y0 = gy + row * sc
        if y0 >= cv.h or y0 + sc <= 0:
            continue
        for col in range(5):
            if line[col] != "1":
                continue
            x0 = gx + col * sc
            for yy in range(max(0, y0), min(cv.h, y0 + sc)):
                o = yy * stride + max(0, x0) * 3
                for xx in range(max(0, x0), min(cv.w, x0 + sc)):
                    buf[o] = r
                    buf[o + 1] = g
                    buf[o + 2] = b
                    o += 3


def draw_text(cv, x, y, s, sc, color, bold=False):
    """Draw s with its cap top at y. `sc` is the integer scale factor
    (1 = 7 px tall, 2 = 14 px, 3 = 21 px, 7 = 49 px). Bold double-strikes
    each glyph a little to the right, thickening the strokes."""
    dx = max(1, sc // 2) if bold else 0
    cx = int(x)
    top = int(y)
    for ch in s:
        g = GLYPHS.get(ord(ch), _MISSING)
        _blit_glyph(cv, cx, top, g, sc, color)
        if dx:
            _blit_glyph(cv, cx + dx, top, g, sc, color)
        cx += g[0] * sc


def wrap_text(cv, text, sc, width):
    """Greedy word wrap; returns lines that fit `width` pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_w(trial, sc) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, text, sc, width, color=INK, spacing=2,
                 max_lines=None, line_h=None):
    """Draw wrapped text; returns (lines_drawn, height_used). If the text
    needs more than max_lines, the last line is cut short with ' ...'."""
    lines = wrap_text(cv, text, sc, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and text_w(lines[-1] + " ...", sc) > width:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = lines[-1] + " ..."
    lh = line_h or int(sc * 9)
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * lh, ln, sc, color)
    return len(lines), len(lines) * lh


# ---------------------------------------------------------------- PNG encoder
# RGB, 8 bit, no interlace. Each scanline is tried with three filters --
# 0 (None), 1 (Sub) and 2 (Up) -- and the one whose bytes sum to the
# smallest total of absolute signed values wins; ties prefer filter 0.
# The result is fully deterministic: same pixels, same bytes.
_ABS = bytes(abs(i if i < 128 else i - 256) for i in range(256))


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def png_bytes(buf, w, h):
    stride = w * 3
    raw = bytearray()
    prev = bytes(stride)
    for y in range(h):
        row = bytes(buf[y * stride:(y + 1) * stride])
        plain = row
        sub = row[:3] + bytes((a - b) & 0xFF for a, b in zip(row[3:], row))
        up = bytes((a - b) & 0xFF for a, b in zip(row, prev))
        s_plain = sum(plain.translate(_ABS))
        s_sub = sum(sub.translate(_ABS))
        s_up = sum(up.translate(_ABS))
        if s_sub < s_plain and s_sub <= s_up:
            raw.append(1)
            raw += sub
        elif s_up < s_plain:
            raw.append(2)
            raw += up
        else:
            raw.append(0)
            raw += plain
        prev = row
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- canvas
class Page:
    """A plain RGB bytearray canvas. Boxes are inclusive on both ends,
    coordinates are truncated to integers, and wide lines grow down (for
    horizontal lines) and right (for vertical lines)."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pitch = w * 3
        self.px = bytearray(bytes(bg) * (w * h))

    def fill(self, x0, y0, x1, y1, color):
        x0 = max(0, int(x0))
        y0 = max(0, int(y0))
        x1 = min(self.w - 1, int(x1))
        y1 = min(self.h - 1, int(y1))
        if x1 < x0 or y1 < y0:
            return
        n = x1 - x0 + 1
        row = bytes(color) * n
        stride = self.pitch
        for y in range(y0, y1 + 1):
            o = y * stride + x0 * 3
            self.px[o:o + 3 * n] = row

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if fill is not None:
            self.fill(x0, y0, x1, y1, fill)
        if outline is not None:
            t = max(1, int(width))
            self.fill(x0, y0, x1, y0 + t - 1, outline)
            self.fill(x0, y1 - t + 1, x1, y1, outline)
            self.fill(x0, y0, x0 + t - 1, y1, outline)
            self.fill(x1 - t + 1, y0, x1, y1, outline)

    def line(self, x0, y0, x1, y1, color, width=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        t = max(1, int(width))
        half = t // 2
        if y0 == y1:
            if x0 > x1:
                x0, x1 = x1, x0
            self.fill(x0, y0, x1, y0 + t - 1, color)
            return
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            self.fill(x0, y0, x0 + t - 1, y1, color)
            return
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill(x0 - half, y0 - half,
                      x0 - half + t - 1, y0 - half + t - 1, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = (x1 - x0) / 2.0
        ry = (y1 - y0) / 2.0
        if rx <= 0 or ry <= 0:
            return
        if fill is not None:
            for y in range(y0, y1 + 1):
                k = (y - cy) / ry
                if -1.0 <= k <= 1.0:
                    dx = rx * math.sqrt(1.0 - k * k)
                    self.fill(int(cx - dx), y, int(cx + dx), y, fill)
        if outline is not None:
            t = max(1, int(width))
            half = t // 2
            per = 2 * math.pi * math.sqrt((rx * rx + ry * ry) / 2.0)
            n = max(24, int(per) + 1)
            for i in range(n + 1):
                a = 2 * math.pi * i / n
                px = int(cx + rx * math.cos(a))
                py = int(cy + ry * math.sin(a))
                self.fill(px - half, py - half,
                          px - half + t - 1, py - half + t - 1, outline)

    def arc(self, x0, y0, x1, y1, start, end, color, width=1):
        # Angles in degrees, 0 = 3 o'clock, increasing clockwise (y down).
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = (x1 - x0) / 2.0
        ry = (y1 - y0) / 2.0
        t = max(1, int(width))
        half = t // 2
        span = end - start
        steps = max(2, int(abs(span) * max(rx, ry) * math.pi / 180.0) + 1)
        for i in range(steps + 1):
            a = math.radians(start + span * i / steps)
            px = int(cx + rx * math.cos(a))
            py = int(cy + ry * math.sin(a))
            self.fill(px - half, py - half,
                      px - half + t - 1, py - half + t - 1, color)

    def polygon(self, pts, fill):
        if not pts:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(self.h - 1, int(math.ceil(max(ys))))
        n = len(pts)
        for y in range(y0, y1 + 1):
            yc = y + 0.5
            xs = []
            for i in range(n):
                xa, ya = pts[i]
                xb, yb = pts[(i + 1) % n]
                if (ya <= yc < yb) or (yb <= yc < ya):
                    f = (yc - ya) / (yb - ya)
                    xs.append(xa + f * (xb - xa))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill(int(xs[i]), y, int(xs[i + 1]), y, fill)


# ---------------------------------------------------------------- the news
# 35 stories, 7 regions. Figures verified 21 Nov 2026; see SOURCES.md.
MASTHEAD_TITLE = "THE GLOBAL FRONT PAGE"
DATE_LINE = "SATURDAY, 21 NOVEMBER 2026"
COUNT_LINE = "35 STORIES  \u00b7  7 REGIONS"

STATS = [
    ("3 MISSILES", "Houthi missiles downed over Riyadh"),
    ("M6.7 QUAKE", "Peru tremor felt in Lima; no deaths"),
    ("\u22125.1% NIKKEI", "Asia's AI rout deepens; Taiex \u22126.2%"),
    ("8 YEARS", "BepiColombo reaches Mercury at last"),
]

LEADS = [
    {
        "kicker": "MIDDLE EAST \u00b7 RIYADH",
        "art": "riyadh",
        "headline": "Three missiles downed over Riyadh as Houthis strike again",
        "deck": "Alert at 01:53, blasts heard, defences hold. Days after the PIF tower was hit.",
        "accent": RED,
    },
    {
        "kicker": "CLIMATE \u00b7 ANTALYA",
        "art": "cop31",
        "headline": "COP31 slips into overtime as fossil-fuel words vanish",
        "deck": "Draft drops fossil fuels and a $120bn finance target; a third text is due today.",
        "accent": TEAL,
    },
    {
        "kicker": "SPACE \u00b7 MERCURY",
        "art": "mercury",
        "headline": "BepiColombo reaches Mercury after an eight-year odyssey",
        "deck": "ESA and JAXA's twin orbiters are captured; science begins in April 2027.",
        "accent": BLUE,
    },
]

CARDS = [
    ("UKRAINE \u00b7 KYIV", "Dawn strike sets Kyiv homes ablaze",
     "Two hurt in Podilskyi; follows a 400-drone barrage that killed eight."),
    ("NATO \u00b7 POLAND", "Missiles land in Poland; Rutte flies in",
     "Kh-101 down in Nowy Lipowiec. Warsaw wants more Eastern Sentry forces."),
    ("AMERICAS \u00b7 PERU", "M6.7 quake shakes the Andes",
     "Tremor near Jun\u00edn at 7:09pm, felt in Lima; no deaths, minor damage."),
    ("SPORT \u00b7 LAS VEGAS", "Antonelli fastest, Verstappen on pole",
     "1:33.893 for the champion \u2014 but a penalty drops him to sixth."),
    ("EUROPE \u00b7 BRUSSELS", "UK and EU seal a reset deal",
     "Food checks end in 2028; 100,000 youth visas a year; \u00a317bn boost."),
    ("MARKETS \u00b7 TOKYO", "AI rout: Nikkei \u22125.1%, Taiex \u22126.2%",
     "SoftBank \u221214.5%. Even Anthropic's $81bn IPO cannot lift tech."),
    ("MIDDLE EAST \u00b7 IRAN", "Trump: Iran wants a \u2018fake deal\u2019",
     "Blockade stays; no strike decision until after the new year."),
    ("DIPLOMACY \u00b7 SHENZHEN", "After the trilateral, a chill",
     "Joint vow: no nuclear arms, free oil shipping. Iran rebuffs it."),
    ("INDIA \u00b7 ODISHA", "Akvan weakens over Odisha",
     "372,000 evacuated, no deaths; restoration under way after landfall."),
    ("GULF \u00b7 HORMUZ", "Tanker hit leaving Hormuz",
     "UKMTO: an oil tanker struck on the stern by an unknown projectile."),
    ("MIDDLE EAST \u00b7 GAZA", "Drone strike injures three in Gaza",
     "Al-Mawasi hit; a man shot dead near Ramallah; 11 choke on gas."),
    ("EUROPE \u00b7 DENMARK", "EU condemns Denmark plot",
     "Alleged Russian-backed plot against a US-Ukrainian citizen."),
]

TIMELINE = [
    ("01:53", "Riyadh alert: three missiles downed."),
    ("MORNING", "Akvan weakens; BepiColombo arrives."),
    ("MIDDAY", "COP31 still deadlocked in overtime."),
    ("AFTERNOON", "Rutte lands in Warsaw; F1 grid set."),
    ("EVENING", "Markets close: Nikkei \u22125.1%, Taiex \u22126.2%."),
]

BRIEF = [
    "Houthi workshops destroyed in Sanaa.",
    "Two missiles to Jazan intercepted.",
    "Houthis threaten to strike Jeddah port.",
    "Air attack reported on Yemen's Mocha port.",
    "Pakistan condemns the attack on Riyadh.",
    "Gillibrand seeks to cut Iran war funding.",
    "SCO forum, day two, opens in Delhi.",
    "NSE now the world's 5th-largest exchange.",
    "Nepal PM Shah visits India 22\u201323 Nov.",
    "Cheetah bears four cubs at Kuno; count 62.",
    "Malaysia to resettle 10,000 Rohingya.",
    "Indonesia fire losses could reach $30bn.",
    "Japan troops to drill live-fire in India.",
    "Delhi air \u2018very poor\u2019; readings over 300.",
    "ICJ: Myanmar guilty of Rohingya genocide.",
    "GTA VI: $3.79bn day-one sales, a record.",
    "Trump\u2013Xi\u2013Putin met in Shenzhen, 19 Nov.",
    "Egypt seals IMF deal; $2.3bn unlocked.",
    "Senegal first to qualify for Afcon 2027.",
    "India\u2013NZ Test, day three in Wellington.",
]

# Schematic world map: (label, x, y) in panel coordinates 0..1,
# plus rough continent blobs as (cx, cy, rx, ry).
MAP_POINTS = [
    ("1 Riyadh", 0.575, 0.46), ("2 Antalya", 0.545, 0.37),
    ("3 Kyiv", 0.505, 0.27), ("4 Warsaw", 0.465, 0.19),
    ("5 Lima", 0.20, 0.66), ("6 Las Vegas", 0.13, 0.36),
    ("7 Brussels", 0.415, 0.22), ("8 Tokyo", 0.845, 0.40),
    ("9 Gopalpur", 0.715, 0.53), ("10 Hormuz", 0.61, 0.47),
]
MAP_BLOBS = [
    (0.17, 0.33, 0.115, 0.085),   # North America
    (0.25, 0.66, 0.055, 0.085),   # South America
    (0.52, 0.60, 0.075, 0.105),   # Africa
    (0.47, 0.26, 0.045, 0.045),   # Europe
    (0.72, 0.35, 0.155, 0.105),   # Asia
    (0.87, 0.78, 0.045, 0.035),   # Australia
]
MAP_LEGEND = [
    "1 Riyadh  \u00b7  2 Antalya  \u00b7  3 Kyiv  \u00b7  4 Warsaw  \u00b7  5 Lima",
    "6 Las Vegas  \u00b7  7 Brussels  \u00b7  8 Tokyo  \u00b7  9 Gopalpur  \u00b7  10 Hormuz",
]


# ---------------------------------------------------------------- art panels
def art_riyadh(pg, x, y, w, h):
    """Riyadh at night: skyline, tall PIF tower, intercept bursts."""
    pg.rect(x, y, x + w, y + h, fill=NIGHT)
    for sx, sy in [(0.07, 0.10), (0.20, 0.05), (0.33, 0.13), (0.48, 0.07),
                   (0.60, 0.12), (0.74, 0.06), (0.88, 0.11), (0.95, 0.22),
                   (0.42, 0.18), (0.12, 0.22)]:
        pg.ellipse(x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1, fill=(215, 215, 195))
    # intercept bursts: dotted trails up to starbursts
    for (tx, ty) in [(0.24, 0.30), (0.55, 0.24), (0.82, 0.32)]:
        bx, by = x + tx * w, y + ty * h
        for k in range(1, 5):
            pg.ellipse(bx - k * 7, by + k * 11 - 1, bx - k * 7 + 2,
                       by + k * 11 + 1, fill=(255, 200, 120))
        for ang in range(0, 360, 45):
            r = 10
            ex = bx + r * math.cos(math.radians(ang))
            ey = by + r * math.sin(math.radians(ang))
            pg.line(bx, by, ex, ey, (255, 170, 60), width=2)
        pg.ellipse(bx - 4, by - 4, bx + 4, by + 4, fill=(255, 220, 140))
    # skyline
    base = y + 0.80 * h
    for bx, bw, bh in [(0.00, 0.07, 0.16), (0.09, 0.06, 0.22), (0.17, 0.08, 0.13),
                       (0.27, 0.06, 0.19), (0.60, 0.07, 0.15), (0.69, 0.06, 0.21),
                       (0.77, 0.07, 0.12), (0.90, 0.08, 0.17)]:
        pg.rect(x + bx * w, base - bh * h, x + (bx + bw) * w, base,
                fill=(8, 10, 18))
    # PIF tower: tall, tapering, lit windows
    tx0, tx1 = x + 0.40 * w, x + 0.52 * w
    pg.polygon([(tx0, base), (tx0 + 0.02 * w, y + 0.34 * h),
                (tx1 - 0.02 * w, y + 0.34 * h), (tx1, base)],
               fill=(10, 12, 22))
    for wy in range(6):
        yy = y + (0.40 + wy * 0.06) * h
        pg.line(tx0 + 0.03 * w, yy, tx1 - 0.03 * w, yy, (255, 210, 110), width=1)
    # ground
    pg.rect(x, base, x + w, y + h, fill=(30, 34, 48))
    pg.rect(x, y, x + w, y + h, outline=(24, 24, 24), width=1)


def art_cop31(pg, x, y, w, h):
    """COP31 hall: globe, sun rays, rows of delegates, draft papers."""
    pg.rect(x, y, x + w, y + h, fill=(238, 240, 226))
    cx, cy = x + 0.62 * w, y + 0.46 * h
    # sun rays
    for k in range(12):
        ang = math.radians(k * 30)
        pg.line(cx + 0.14 * w * math.cos(ang), cy + 0.14 * h * math.sin(ang) * 1.4,
                cx + 0.21 * w * math.cos(ang), cy + 0.21 * h * math.sin(ang) * 1.4,
                (232, 190, 90), width=3)
    # globe
    pg.ellipse(cx - 0.11 * w, cy - 0.11 * w, cx + 0.11 * w, cy + 0.11 * w,
               fill=TEAL, outline=(10, 70, 70), width=2)
    pg.arc(cx - 0.11 * w, cy - 0.11 * w, cx + 0.11 * w, cy + 0.11 * w,
           200, 340, (120, 200, 190), width=5)
    pg.arc(cx - 0.065 * w, cy - 0.11 * w, cx + 0.065 * w, cy + 0.11 * w,
           90, 270, (120, 200, 190), width=3)
    pg.line(cx - 0.11 * w, cy, cx + 0.11 * w, cy, (120, 200, 190), width=3)
    # delegate rows
    for row in range(3):
        yy = y + (0.72 + row * 0.09) * h
        for k in range(9):
            px = x + (0.06 + k * 0.11) * w
            pg.ellipse(px - 4, yy - 4, px + 4, yy + 4,
                       fill=(60, 60, 60) if k % 2 else (140, 40, 50))
    # draft paper strip, crossed out
    pg.rect(x + 0.04 * w, y + 0.07 * h, x + 0.48 * w, y + 0.19 * h,
            fill=WHITE, outline=(24, 24, 24), width=1)
    draw_text(pg, x + 0.06 * w, y + 0.09 * h, "DRAFT: FOSSIL FUELS",
              1, INK, bold=True)
    pg.line(x + 0.05 * w, y + 0.145 * h, x + 0.47 * w, y + 0.125 * h,
            RED, width=2)
    pg.rect(x, y, x + w, y + h, outline=(24, 24, 24), width=1)


def art_mercury(pg, x, y, w, h):
    """Mercury: cratered planet, twin orbiters, orbit ellipse, stars."""
    pg.rect(x, y, x + w, y + h, fill=SPACE)
    for sx, sy in [(0.06, 0.10), (0.16, 0.06), (0.30, 0.08), (0.52, 0.05),
                   (0.68, 0.09), (0.84, 0.06), (0.93, 0.16), (0.08, 0.28),
                   (0.90, 0.30), (0.40, 0.14)]:
        pg.ellipse(x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1, fill=(225, 225, 215))
    # orbit ellipse
    cx, cy = x + 0.44 * w, y + 0.56 * h
    pg.ellipse(x + 0.06 * w, y + 0.18 * h, x + 0.82 * w, y + 0.92 * h,
               outline=(120, 130, 160), width=2)
    # planet
    r = 0.19 * w
    pg.ellipse(cx - r, cy - r, cx + r, cy + r, fill=(168, 158, 142),
               outline=(110, 100, 84), width=2)
    for (ox, oy, orr) in [(-0.06, -0.05, 9), (0.07, 0.03, 12), (-0.02, 0.08, 7),
                          (0.10, -0.08, 6), (-0.11, 0.04, 5), (0.03, -0.11, 8)]:
        pg.ellipse(cx + ox * w - orr, cy + oy * w - orr,
                   cx + ox * w + orr, cy + oy * w + orr,
                   outline=(120, 110, 94), width=1)
    # spacecraft on the orbit
    sx, sy = x + 0.74 * w, y + 0.28 * h
    pg.rect(sx - 4, sy - 4, sx + 4, sy + 4, fill=(235, 235, 235))
    pg.rect(sx - 20, sy - 2, sx - 5, sy + 2, fill=(60, 110, 180))
    pg.rect(sx + 5, sy - 2, sx + 20, sy + 2, fill=(60, 110, 180))
    draw_text(pg, x + 0.06 * w, y + 0.06 * h, "8 YEARS \u00b7 10 BN KM",
              1, (220, 220, 210), bold=True)
    pg.rect(x, y, x + w, y + h, outline=(24, 24, 24), width=1)


ART = {"riyadh": art_riyadh, "cop31": art_cop31, "mercury": art_mercury}


# ---------------------------------------------------------------- sections
# Type sizes are integer scales of the 5x7 hand font: 7 for the nameplate,
# 3 for the big stat figures, 2 for kickers, headlines and section rules,
# 1 for decks, labels and the brief strip. Bold is a double strike.
def section_rule(pg, x, y, w, label):
    draw_text(pg, x, y, label, 2, INK, bold=True)
    tw = text_w(label, 2)
    pg.line(x + tw + 8, y + 7, x + w, y + 7, RULE, width=1)


def draw_masthead(pg):
    pg.rect(0, 0, W, H, fill=PAPER)
    pg.line(24, 12, W - 24, 12, RULE, width=2)
    pg.line(24, 16, W - 24, 16, RULE, width=1)
    draw_text(pg, 24, 22, "EST. 2026 \u00b7 INDEPENDENT", 1, INK_SOFT)
    right = "ONE DAY \u00b7 ONE PAGE \u00b7 THE WHOLE WORLD"
    draw_text(pg, W - 24 - text_w(right, 1), 22, right, 1, INK_SOFT)
    t = MASTHEAD_TITLE
    draw_text(pg, (W - text_w(t, 7)) / 2, 38, t, 7, INK, bold=True)
    pg.rect(24, 100, W - 24, 128, fill=INK)
    draw_text(pg, 36, 107, DATE_LINE, 2, WHITE, bold=True)
    cw = text_w(COUNT_LINE, 2)
    draw_text(pg, W - 36 - cw, 107, COUNT_LINE, 2, WHITE, bold=True)


def draw_stats(pg):
    y0, y1, x0 = 138, 182, 24
    w = (W - 48 - 3 * 10) / 4
    for i, (big, lab) in enumerate(STATS):
        x = x0 + i * (w + 10)
        pg.rect(x, y0, x + w, y1, outline=GREY_LINE, width=1, fill=CREAM)
        pg.rect(x, y0, x + w, y0 + 3, fill=RED)
        draw_text(pg, x + 10, y0 + 9, big, 3, RED_DARK, bold=True)
        draw_wrapped(pg, x + 10, y0 + 32, lab, 1, w - 20, color=INK_SOFT,
                     max_lines=1, line_h=10)


def draw_lead(pg, x, y, w, lead):
    art_h = 122
    ART[lead["art"]](pg, x, y, w, art_h)
    yy = y + art_h + 8
    draw_text(pg, x, yy, lead["kicker"], 2, lead["accent"], bold=True)
    yy += 15
    pg.line(x, yy, x + w, yy, GREY_LINE, width=1)
    yy += 6
    _, used = draw_wrapped(pg, x, yy, lead["headline"], 2, w, max_lines=2,
                           line_h=18)
    yy += used + 4
    draw_wrapped(pg, x, yy, lead["deck"], 1, w, max_lines=2, line_h=10)


def draw_card(pg, x, y, w, h, kicker, headline, deck, idx):
    pg.rect(x, y, x + w, y + h, outline=GREY_LINE, width=1, fill=CREAM)
    pg.rect(x, y, x + 4, y + h, fill=RED if idx % 3 == 0 else
            (BLUE if idx % 3 == 1 else TEAL))
    tx = x + 12
    draw_text(pg, tx, y + 7, kicker, 2, INK_SOFT, bold=True)
    _, used = draw_wrapped(pg, tx, y + 22, headline, 2, w - 22,
                           max_lines=2, line_h=18)
    draw_wrapped(pg, tx, y + 22 + used + 2, deck, 1, w - 22,
                 color=INK_SOFT, max_lines=2, line_h=10)


def draw_map(pg, x, y, w, h):
    pg.rect(x, y, x + w, y + h, outline=GREY_LINE, width=1, fill=MAP_SEA)
    section_rule(pg, x + 10, y + 8, w - 20, "THE WORLD AT A GLANCE \u2014 SCHEMATIC MAP")
    my = y + 30
    mh = h - 30 - 34
    for gx in (0.25, 0.5, 0.75):
        pg.line(x + gx * w, my, x + gx * w, my + mh, (200, 212, 220), width=1)
    for gy in (0.33, 0.66):
        pg.line(x, my + gy * mh, x + w, my + gy * mh, (200, 212, 220), width=1)
    for (cx, cy, rx, ry) in MAP_BLOBS:
        pg.ellipse(x + (cx - rx) * w, my + (cy - ry) * mh,
                   x + (cx + rx) * w, my + (cy + ry) * mh, fill=MAP_LAND,
                   outline=(160, 170, 150), width=1)
    for label, px, py in MAP_POINTS:
        num, _name = label.split(" ", 1)
        dx, dy = x + px * w, my + py * mh
        pg.ellipse(dx - 8, dy - 8, dx + 8, dy + 8, fill=RED, outline=WHITE, width=1)
        tw = text_w(num, 1)
        draw_text(pg, dx - tw / 2, dy - 4, num, 1, WHITE, bold=True)
    ly = my + mh + 6
    for i, line in enumerate(MAP_LEGEND):
        draw_text(pg, x + 10, ly + i * 11, line, 1, INK_SOFT)


def draw_right(pg, x, y, w):
    section_rule(pg, x, y, w, "THE DAY IN ORDER")
    yy = y + 24
    for when, what in TIMELINE:
        draw_text(pg, x, yy, when, 1, RED_DARK, bold=True)
        _, used = draw_wrapped(pg, x + 78, yy, what, 1, w - 78, color=INK,
                               max_lines=2, line_h=10)
        yy += max(used, 10) + 9
    return yy


def draw_brief_strip(pg, x, y, w):
    section_rule(pg, x, y, w, "IN BRIEF")
    yy = y + 20
    col_w = (w - 3 * 14) / 4
    for i, item in enumerate(BRIEF):
        cx = x + (i % 4) * (col_w + 14)
        cy = yy + (i // 4) * 14
        draw_text(pg, cx, cy, "\u25aa ", 1, RED)
        draw_wrapped(pg, cx + 11, cy, item, 1, col_w - 11, color=INK_SOFT,
                     max_lines=1, line_h=10)


def draw_footer(pg):
    line = ("All stories reported on Saturday 21 November 2026 \u00b7 Figures as reported by "
            "Reuters, AP, Al Jazeera, Arab News, ESA, FIA, IMD and ISW \u00b7 THE GLOBAL FRONT PAGE")
    draw_text(pg, (W - text_w(line, 1)) / 2, H - 12, line, 1, INK_SOFT)


# ---------------------------------------------------------------- assemble
def build():
    pg = Page(W, H, PAPER)
    draw_masthead(pg)
    draw_stats(pg)
    # leads
    lx, ly, lw, gap = 24, 190, (W - 48 - 2 * 10) / 3, 10
    for i, lead in enumerate(LEADS):
        draw_lead(pg, lx + i * (lw + gap), ly, lw, lead)
    # cards
    section_rule(pg, 24, 438, W - 48, "INSIDE TODAY")
    cw, ch, cg = (W - 48 - 3 * 8) / 4, 90, 8
    for i, (kick, head, deck) in enumerate(CARDS):
        cx = 24 + (i % 4) * (cw + cg)
        cy = 460 + (i // 4) * (ch + cg)
        draw_card(pg, cx, cy, cw, ch, kick, head, deck, i)
    # bottom row: map + timeline
    by = 758
    draw_map(pg, 24, by, 620, 152)
    draw_right(pg, 656, by, 344)
    # brief strip
    draw_brief_strip(pg, 24, 918, W - 48)
    pg.line(24, 1006, W - 24, 1006, RULE, width=1)
    draw_footer(pg)
    return pg


def main():
    pg = build()
    data = png_bytes(pg.px, W, H)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
