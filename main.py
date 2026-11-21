#!/usr/bin/env python3
"""THE GLOBAL FRONT PAGE -- Saturday 21 November 2026.

A deterministic program that draws a one-page newspaper front page
summing up the world's news of Saturday 21 November 2026 and writes it
to /output/entry.png (1024x1024, PNG, <= 1 MiB).

Every story, date and figure below was verified against live reporting
on 21 November 2026 (Reuters, AP, Al Jazeera, Arab News, ESA, FIA, IMD,
ISW and others); see SOURCES.md for the source of each fact. No network
access, no clock, no randomness: the same run always writes the same bytes.

Run:  python3 main.py            (writes /output/entry.png)
      OUTPUT_DIR=out python3 main.py   (writes out/entry.png, for local tests)
Requires: Pillow (PIL). Standard library otherwise.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.environ.get("OUTPUT_DIR", "/output"), "entry.png")

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

# ---------------------------------------------------------------- fonts
_FONT_DIRS = [
    "/usr/share/fonts/truetype/liberation/",
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/noto/",
]


def _find(names):
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


_SERIF_B = _find(["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"])
_SERIF = _find(["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"])
_SANS = _find(["LiberationSans-Regular.ttf", "DejaVuSans.ttf"])
_SANS_B = _find(["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"])


def font(kind, size):
    path = {
        "serif_b": _SERIF_B, "serif": _SERIF,
        "sans": _SANS, "sans_b": _SANS_B,
    }.get(kind) or _SANS
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------- text tools
def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill=INK, spacing=2,
                 max_lines=None, line_h=None):
    """Draw wrapped text; returns (lines_drawn, height_used)."""
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > width:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = lines[-1] + " ..."
    lh = line_h or int(fnt.size * 1.22)
    for i, ln in enumerate(lines):
        draw.text((x, y + i * lh), ln, font=fnt, fill=fill)
    return len(lines), len(lines) * lh


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
def art_riyadh(d, x, y, w, h):
    """Riyadh at night: skyline, tall PIF tower, intercept bursts."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx, sy in [(0.07, 0.10), (0.20, 0.05), (0.33, 0.13), (0.48, 0.07),
                   (0.60, 0.12), (0.74, 0.06), (0.88, 0.11), (0.95, 0.22),
                   (0.42, 0.18), (0.12, 0.22)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                  fill=(215, 215, 195))
    # intercept bursts: dotted trails up to starbursts
    for (tx, ty) in [(0.24, 0.30), (0.55, 0.24), (0.82, 0.32)]:
        bx, by = x + tx * w, y + ty * h
        for k in range(1, 5):
            d.ellipse([bx - k * 7, by + k * 11 - 1, bx - k * 7 + 2,
                       by + k * 11 + 1], fill=(255, 200, 120))
        for ang in range(0, 360, 45):
            import math
            r = 10
            ex = bx + r * math.cos(math.radians(ang))
            ey = by + r * math.sin(math.radians(ang))
            d.line([bx, by, ex, ey], fill=(255, 170, 60), width=2)
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 220, 140))
    # skyline
    base = y + 0.80 * h
    for bx, bw, bh in [(0.00, 0.07, 0.16), (0.09, 0.06, 0.22), (0.17, 0.08, 0.13),
                       (0.27, 0.06, 0.19), (0.60, 0.07, 0.15), (0.69, 0.06, 0.21),
                       (0.77, 0.07, 0.12), (0.90, 0.08, 0.17)]:
        d.rectangle([x + bx * w, base - bh * h, x + (bx + bw) * w, base],
                    fill=(8, 10, 18))
    # PIF tower: tall, tapering, lit windows
    tx0, tx1 = x + 0.40 * w, x + 0.52 * w
    d.polygon([(tx0, base), (tx0 + 0.02 * w, y + 0.34 * h),
               (tx1 - 0.02 * w, y + 0.34 * h), (tx1, base)], fill=(10, 12, 22))
    for wy in range(6):
        yy = y + (0.40 + wy * 0.06) * h
        d.line([tx0 + 0.03 * w, yy, tx1 - 0.03 * w, yy], fill=(255, 210, 110), width=1)
    # ground
    d.rectangle([x, base, x + w, y + h], fill=(30, 34, 48))
    d.rectangle([x, y, x + w, y + h], outline=(24, 24, 24), width=1)


def art_cop31(d, x, y, w, h):
    """COP31 hall: globe, sun rays, rows of delegates, draft papers."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 226))
    cx, cy = x + 0.62 * w, y + 0.46 * h
    # sun rays
    import math
    for k in range(12):
        ang = math.radians(k * 30)
        d.line([cx + 0.14 * w * math.cos(ang), cy + 0.14 * h * math.sin(ang) * 1.4,
                cx + 0.21 * w * math.cos(ang), cy + 0.21 * h * math.sin(ang) * 1.4],
               fill=(232, 190, 90), width=3)
    # globe
    d.ellipse([cx - 0.11 * w, cy - 0.11 * w, cx + 0.11 * w, cy + 0.11 * w],
              fill=TEAL, outline=(10, 70, 70), width=2)
    d.arc([cx - 0.11 * w, cy - 0.11 * w, cx + 0.11 * w, cy + 0.11 * w],
          start=200, end=340, fill=(120, 200, 190), width=5)
    d.arc([cx - 0.065 * w, cy - 0.11 * w, cx + 0.065 * w, cy + 0.11 * w],
          start=90, end=270, fill=(120, 200, 190), width=3)
    d.line([cx - 0.11 * w, cy, cx + 0.11 * w, cy], fill=(120, 200, 190), width=3)
    # delegate rows
    for row in range(3):
        yy = y + (0.72 + row * 0.09) * h
        for k in range(9):
            px = x + (0.06 + k * 0.11) * w
            d.ellipse([px - 4, yy - 4, px + 4, yy + 4],
                      fill=(60, 60, 60) if k % 2 else (140, 40, 50))
    # draft paper strip, crossed out
    d.rectangle([x + 0.04 * w, y + 0.07 * h, x + 0.48 * w, y + 0.19 * h],
                fill=WHITE, outline=(24, 24, 24), width=1)
    d.text((x + 0.06 * w, y + 0.09 * h), "DRAFT: FOSSIL FUELS",
           font=font("sans_b", 10), fill=INK)
    d.line([x + 0.05 * w, y + 0.145 * h, x + 0.47 * w, y + 0.125 * h],
           fill=RED, width=2)
    d.rectangle([x, y, x + w, y + h], outline=(24, 24, 24), width=1)


def art_mercury(d, x, y, w, h):
    """Mercury: cratered planet, twin orbiters, orbit ellipse, stars."""
    d.rectangle([x, y, x + w, y + h], fill=SPACE)
    for sx, sy in [(0.06, 0.10), (0.16, 0.06), (0.30, 0.08), (0.52, 0.05),
                   (0.68, 0.09), (0.84, 0.06), (0.93, 0.16), (0.08, 0.28),
                   (0.90, 0.30), (0.40, 0.14)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                  fill=(225, 225, 215))
    # orbit ellipse
    cx, cy = x + 0.44 * w, y + 0.56 * h
    d.ellipse([x + 0.06 * w, y + 0.18 * h, x + 0.82 * w, y + 0.92 * h],
              outline=(120, 130, 160), width=2)
    # planet
    r = 0.19 * w
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 158, 142),
              outline=(110, 100, 84), width=2)
    for (ox, oy, orr) in [(-0.06, -0.05, 9), (0.07, 0.03, 12), (-0.02, 0.08, 7),
                          (0.10, -0.08, 6), (-0.11, 0.04, 5), (0.03, -0.11, 8)]:
        d.ellipse([cx + ox * w - orr, cy + oy * w - orr,
                   cx + ox * w + orr, cy + oy * w + orr],
                  outline=(120, 110, 94), width=1)
    # spacecraft on the orbit
    sx, sy = x + 0.74 * w, y + 0.28 * h
    d.rectangle([sx - 4, sy - 4, sx + 4, sy + 4], fill=(235, 235, 235))
    d.rectangle([sx - 20, sy - 2, sx - 5, sy + 2], fill=(60, 110, 180))
    d.rectangle([sx + 5, sy - 2, sx + 20, sy + 2], fill=(60, 110, 180))
    d.text((x + 0.06 * w, y + 0.06 * h), "8 YEARS \u00b7 10 BN KM",
           font=font("sans_b", 10), fill=(220, 220, 210))
    d.rectangle([x, y, x + w, y + h], outline=(24, 24, 24), width=1)


ART = {"riyadh": art_riyadh, "cop31": art_cop31, "mercury": art_mercury}


# ---------------------------------------------------------------- sections
def section_rule(d, x, y, w, label):
    f = font("sans_b", 11)
    d.text((x, y), label, font=f, fill=INK)
    tw = d.textlength(label, font=f)
    d.line([x + tw + 8, y + 7, x + w, y + 7], fill=RULE, width=1)


def draw_masthead(d):
    d.rectangle([0, 0, W, H], fill=PAPER)
    d.line([24, 12, W - 24, 12], fill=RULE, width=2)
    d.line([24, 16, W - 24, 16], fill=RULE, width=1)
    f_small = font("sans", 11)
    d.text((24, 22), "EST. 2026 \u00b7 INDEPENDENT", font=f_small, fill=INK_SOFT)
    right = "ONE DAY \u00b7 ONE PAGE \u00b7 THE WHOLE WORLD"
    d.text((W - 24 - d.textlength(right, font=f_small), 22), right,
           font=f_small, fill=INK_SOFT)
    f_title = font("serif_b", 52)
    t = MASTHEAD_TITLE
    d.text(((W - d.textlength(t, font=f_title)) / 2, 38), t, font=f_title, fill=INK)
    d.rectangle([24, 100, W - 24, 128], fill=INK)
    f_date = font("sans_b", 15)
    d.text((36, 107), DATE_LINE, font=f_date, fill=WHITE)
    cw = d.textlength(COUNT_LINE, font=f_date)
    d.text((W - 36 - cw, 107), COUNT_LINE, font=f_date, fill=WHITE)


def draw_stats(d):
    y0, y1, x0 = 138, 182, 24
    w = (W - 48 - 3 * 10) / 4
    f_big = font("sans_b", 19)
    f_lab = font("sans", 11)
    for i, (big, lab) in enumerate(STATS):
        x = x0 + i * (w + 10)
        d.rectangle([x, y0, x + w, y1], outline=GREY_LINE, width=1, fill=CREAM)
        d.rectangle([x, y0, x + w, y0 + 3], fill=RED)
        d.text((x + 10, y0 + 9), big, font=f_big, fill=RED_DARK)
        draw_wrapped(d, x + 10, y0 + 29, lab, f_lab, w - 20, fill=INK_SOFT,
                     max_lines=1, line_h=12)


def draw_lead(d, x, y, w, lead):
    art_h = 122
    ART[lead["art"]](d, x, y, w, art_h)
    yy = y + art_h + 8
    f_kick = font("sans_b", 10)
    d.text((x, yy), lead["kicker"], font=f_kick, fill=lead["accent"])
    yy += 15
    d.line([x, yy, x + w, yy], fill=GREY_LINE, width=1)
    yy += 6
    f_head = font("serif_b", 20)
    _, used = draw_wrapped(d, x, yy, lead["headline"], f_head, w, max_lines=2,
                           line_h=24)
    yy += used + 4
    f_deck = font("sans", 12)
    draw_wrapped(d, x, yy, lead["deck"], f_deck, w, max_lines=2, line_h=15)


def draw_card(d, x, y, w, h, kicker, headline, deck, idx):
    d.rectangle([x, y, x + w, y + h], outline=GREY_LINE, width=1, fill=CREAM)
    d.rectangle([x, y, x + 4, y + h], fill=RED if idx % 3 == 0 else
                (BLUE if idx % 3 == 1 else TEAL))
    tx = x + 12
    f_kick = font("sans_b", 9)
    d.text((tx, y + 7), kicker, font=f_kick, fill=INK_SOFT)
    f_head = font("serif_b", 13)
    _, used = draw_wrapped(d, tx, y + 22, headline, f_head, w - 22,
                           max_lines=2, line_h=16)
    f_deck = font("sans", 11)
    draw_wrapped(d, tx, y + 22 + used + 2, deck, f_deck, w - 22,
                 fill=INK_SOFT, max_lines=2, line_h=13)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=GREY_LINE, width=1, fill=MAP_SEA)
    section_rule(d, x + 10, y + 8, w - 20, "THE WORLD AT A GLANCE \u2014 SCHEMATIC MAP")
    my = y + 30
    mh = h - 30 - 34
    for gx in (0.25, 0.5, 0.75):
        d.line([x + gx * w, my, x + gx * w, my + mh], fill=(200, 212, 220), width=1)
    for gy in (0.33, 0.66):
        d.line([x, my + gy * mh, x + w, my + gy * mh], fill=(200, 212, 220), width=1)
    for (cx, cy, rx, ry) in MAP_BLOBS:
        d.ellipse([x + (cx - rx) * w, my + (cy - ry) * mh,
                   x + (cx + rx) * w, my + (cy + ry) * mh], fill=MAP_LAND,
                  outline=(160, 170, 150), width=1)
    f_dot = font("sans_b", 9)
    for label, px, py in MAP_POINTS:
        num, _name = label.split(" ", 1)
        dx, dy = x + px * w, my + py * mh
        d.ellipse([dx - 8, dy - 8, dx + 8, dy + 8], fill=RED, outline=WHITE, width=1)
        tw = d.textlength(num, font=f_dot)
        d.text((dx - tw / 2, dy - 6), num, font=f_dot, fill=WHITE)
    ly = my + mh + 6
    f_leg = font("sans", 10)
    for i, line in enumerate(MAP_LEGEND):
        d.text((x + 10, ly + i * 13), line, font=f_leg, fill=INK_SOFT)


def draw_right(d, x, y, w):
    section_rule(d, x, y, w, "THE DAY IN ORDER")
    yy = y + 24
    f_t = font("sans_b", 11)
    f_b = font("sans", 11)
    for when, what in TIMELINE:
        d.text((x, yy), when, font=f_t, fill=RED_DARK)
        _, used = draw_wrapped(d, x + 78, yy, what, f_b, w - 78, fill=INK,
                               max_lines=2, line_h=13)
        yy += max(used, 13) + 9
    return yy


def draw_brief_strip(d, x, y, w):
    section_rule(d, x, y, w, "IN BRIEF")
    yy = y + 20
    f_br = font("sans", 10)
    col_w = (w - 3 * 14) / 4
    for i, item in enumerate(BRIEF):
        cx = x + (i % 4) * (col_w + 14)
        cy = yy + (i // 4) * 14
        d.text((cx, cy), "\u25aa ", font=f_br, fill=RED)
        draw_wrapped(d, cx + 11, cy, item, f_br, col_w - 11, fill=INK_SOFT,
                     max_lines=1, line_h=12)


def draw_footer(d):
    f = font("sans", 9)
    line = ("All stories reported on Saturday 21 November 2026 \u00b7 Figures as reported by "
            "Reuters, AP, Al Jazeera, Arab News, ESA, FIA, IMD and ISW \u00b7 THE GLOBAL FRONT PAGE")
    d.text(((W - d.textlength(line, font=f)) / 2, H - 12), line, font=f,
           fill=INK_SOFT)


# ---------------------------------------------------------------- assemble
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    # leads
    lx, ly, lw, gap = 24, 190, (W - 48 - 2 * 10) / 3, 10
    for i, lead in enumerate(LEADS):
        draw_lead(d, lx + i * (lw + gap), ly, lw, lead)
    # cards
    section_rule(d, 24, 438, W - 48, "INSIDE TODAY")
    cw, ch, cg = (W - 48 - 3 * 8) / 4, 90, 8
    for i, (kick, head, deck) in enumerate(CARDS):
        cx = 24 + (i % 4) * (cw + cg)
        cy = 460 + (i // 4) * (ch + cg)
        draw_card(d, cx, cy, cw, ch, kick, head, deck, i)
    # bottom row: map + timeline
    by = 758
    draw_map(d, 24, by, 620, 152)
    draw_right(d, 656, by, 344)
    # brief strip
    draw_brief_strip(d, 24, 918, W - 48)
    d.line([24, 1006, W - 24, 1006], fill=RULE, width=1)
    draw_footer(d)
    return img


def main():
    img = build()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
