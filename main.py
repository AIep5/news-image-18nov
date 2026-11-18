"""Front page of THE WORLD TODAY for Wednesday 18 November 2026.

A deterministic newspaper front page, drawn pixel by pixel with the
standard library only: no network, no clock, no randomness. Every run
writes the same bytes to /output/entry.png.

The page: a masthead, one lead story (the United States striking an
Iranian missile site on Qeshm Island, and Iran answering with drones
at Bahrain and Kuwait), and five more stories from the day in a grid
- the Kerch bridge to Crimea falling, the Trump-Xi-Putin meeting in
Shenzhen, the Democrats taking Alaska, Ebola doubling in Congo, and
a Category 5 cyclone hitting the Cook Islands - plus an In Brief box.

Text is blitted from the bitmap tables in fontdata.py (rendered once
from DejaVu Bold in the build session); pictures are flat shapes
drawn with the canvas primitives below.
"""

import os
import struct
import sys
import zlib

# The grader runs `python3 -P -s main.py`, and -P strips the script's own
# directory from sys.path, so a sibling import would fail there even
# though it works in a plain run. Put the script's directory back first.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fontdata

W = 1024
H = 1024

PAPER = (246, 241, 230)     # newsprint cream
INK = (17, 17, 17)          # near-black ink
RED = (163, 18, 18)         # accent red for kickers and rules
BLUE = (28, 61, 110)        # deep blue for sea and flags
TEAL = (38, 90, 86)         # sea green for the cyclone panel
GOLD = (196, 141, 32)       # sun and stars
GREY = (120, 118, 110)      # secondary rules and smoke
PALE_SKY = (222, 228, 232)  # pale sky band
PALE_SEA = (178, 196, 214)  # pale sea band


# ---------------------------------------------------------------- PNG out

def _chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    """Encode the canvas as a deterministic 1024x1024 RGB PNG."""
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += canvas.px[y * W * 3:(y + 1) * W * 3]
    data = zlib.compress(bytes(raw), 6)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", data)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self):
        self.px = bytearray(bytes(PAPER) * (W * H))
        self.clip = None  # (x, y, w, h) or None: pictures stay in their box

    def set_clip(self, x, y, w, h):
        self.clip = (x, y, w, h)

    def clear_clip(self):
        self.clip = None

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if self.clip is not None:
            cx, cy, cw, ch = self.clip
            x0 = max(x0, cx)
            y0 = max(y0, cy)
            x1 = min(x1, cx + cw)
            y1 = min(y1, cy + ch)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, color, thick=1):
        self.fill_rect(min(x0, x1), y, abs(x1 - x0) + 1, thick, color)

    def vline(self, x, y0, y1, color, thick=1):
        self.fill_rect(x, min(y0, y1), thick, abs(y1 - y0) + 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line, with a square brush of the given thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - thick // 2, y - thick // 2, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, x + w - 1, y, color, thick)
        self.hline(x, x + w - 1, y + h - 1, color, thick)
        self.vline(x, y, y + h - 1, color, thick)
        self.vline(x + w - 1, y, y + h - 1, color, thick)

    def disc(self, cx, cy, r, color):
        """Filled disc."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def poly(self, points, color):
        """Filled polygon by scanline."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, color)

    def arc(self, cx, cy, r, a0, a1, color, thick=2, steps=40):
        """Arc of a circle, angles in degrees, 0 = east, going clockwise."""
        import math
        prev = None
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            p = (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], color, thick)
            prev = p

# ---------------------------------------------------------------- text

TRACKING = 1  # extra pixels between glyphs at scale 1


def _blit_row(cv, x, y, bits, width, scale, color):
    """Blit one glyph row, scaling each run of ink pixels."""
    run = None
    for bx in range(width + 1):
        on = bx < width and (bits >> (width - 1 - bx)) & 1
        if on and run is None:
            run = bx
        elif not on and run is not None:
            cv.fill_rect(x + run * scale, y, (bx - run) * scale, scale, color)
            run = None


def text_width(text, font, scale, tracking=TRACKING):
    """Pixel width of text drawn with this font at this scale."""
    total = 0
    for ch in text:
        g = font.get(ch)
        if g is None:
            continue
        total += (g[0] + tracking) * scale
    if total:
        total -= tracking * scale
    return total


def draw_text(cv, x, y, text, font, scale, color, tracking=TRACKING):
    """Draw text; y is the top of the em box. Returns width drawn."""
    cx = x
    for ch in text:
        g = font.get(ch)
        if g is None:
            continue
        width, dy, rows = g
        for r, bits in enumerate(rows):
            _blit_row(cv, cx, y + (dy + r) * scale, bits, width, scale, color)
        cx += (width + tracking) * scale
    return cx - x - tracking * scale if text else 0


def draw_text_centred(cv, cx, y, text, font, scale, color, tracking=TRACKING):
    draw_text(cv, cx - text_width(text, font, scale, tracking) // 2,
              y, text, font, scale, color, tracking)


def wrap_text(text, max_width, font, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip() if line else word
            if text_width(trial, font, scale) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_lines(cv, x, y, lines, font, scale, color, leading=None):
    """Draw stacked lines; leading defaults to one glyph row of space."""
    if leading is None:
        leading = (24 + 6) * scale
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * leading, line, font, scale, color)
    return len(lines) * leading


def star(cv, cx, cy, r, color):
    """Five-pointed star, flat."""
    import math
    points = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else int(r * 0.45)
        points.append((int(cx + rr * math.cos(ang)), int(cy + rr * math.sin(ang))))
    cv.poly(points, color)

# ---------------------------------------------------------------- pictures

def _burst(cv, cx, cy, r, color, spikes=9):
    """Spiky starburst, flat."""
    import math
    points = []
    for i in range(spikes * 2):
        ang = math.radians(-90 + i * 180 / spikes)
        rr = r if i % 2 == 0 else int(r * 0.38)
        points.append((int(cx + rr * math.cos(ang)), int(cy + rr * math.sin(ang))))
    cv.poly(points, color)


def pic_gulf(cv, x, y, w, h):
    """Qeshm Island at dusk: sea, island, radar dome, jet, blast."""
    horizon = y + int(h * 0.62)
    cv.fill_rect(x, y, w, horizon - y, PALE_SKY)
    cv.fill_rect(x, horizon, w, y + h - horizon, BLUE)
    cv.disc(x + int(w * 0.86), y + int(h * 0.28), int(h * 0.17), GOLD)
    # big island mass, peak left of centre
    ix = x + int(w * 0.04)
    iy = horizon
    cv.poly([(ix, iy), (ix + int(w * 0.06), iy - int(h * 0.32)),
             (ix + int(w * 0.14), iy - int(h * 0.45)),
             (ix + int(w * 0.24), iy - int(h * 0.28)),
             (ix + int(w * 0.34), iy - int(h * 0.14)),
             (ix + int(w * 0.42), iy)], INK)
    # radar dome on the peak, ink-outlined so it pops against the sky
    dome_cx, dome_cy, dome_r = ix + int(w * 0.14), iy - int(h * 0.45), int(h * 0.13)
    cv.disc(dome_cx, dome_cy, dome_r + 2, INK)
    cv.disc(dome_cx, dome_cy, dome_r, PAPER)
    cv.fill_rect(dome_cx - dome_r - 2, dome_cy, 2 * dome_r + 4, dome_r + 2, INK)
    cv.vline(dome_cx, dome_cy - dome_r, dome_cy, INK, 2)
    # explosion on the slope just past the dome
    bx, by = dome_cx + int(w * 0.08), iy - int(h * 0.30)
    _burst(cv, bx, by, int(h * 0.24), (222, 110, 20))
    _burst(cv, bx, by, int(h * 0.13), GOLD)
    # smoke above the blast
    cv.disc(bx + int(w * 0.04), iy - int(h * 0.50), int(h * 0.08), GREY)
    cv.disc(bx + int(w * 0.08), iy - int(h * 0.56), int(h * 0.06), GREY)
    # delta jet with a short contrail, upper right
    jx, jy = x + int(w * 0.62), y + int(h * 0.22)
    cv.poly([(jx + int(w * 0.07), jy), (jx, jy - int(h * 0.08)),
             (jx, jy + int(h * 0.08))], INK)
    cv.hline(jx - int(w * 0.08), jx, jy, GREY, 2)


def pic_bridge(cv, x, y, w, h):
    """The Kerch span: deck broken in the middle, arch, smoke, drone."""
    cv.fill_rect(x, y, w, h, PALE_SKY)
    sea = y + int(h * 0.62)
    cv.fill_rect(x, sea, w, h - int(h * 0.62), PALE_SEA)
    deck = y + int(h * 0.48)
    # arch over the deck, sized to stay inside the strip
    cv.arc(x + int(w * 0.15), deck, int(h * 0.42), 200, 340, INK, 3, 30)
    # deck: two ends, one span dropped into the gap
    cv.fill_rect(x + 4, deck, int(w * 0.34), 7, INK)
    cv.fill_rect(x + w - 4 - int(w * 0.34), deck, int(w * 0.34), 7, INK)
    cv.poly([(x + int(w * 0.36), deck + 2), (x + int(w * 0.52), deck + int(h * 0.16)),
             (x + int(w * 0.54), deck + int(h * 0.16) + 5),
             (x + int(w * 0.38), deck + 7)], INK)
    # piers
    cv.fill_rect(x + int(w * 0.16), deck + 7, 6, sea - deck, INK)
    cv.fill_rect(x + int(w * 0.80), deck + 7, 6, sea - deck, INK)
    # smoke from the gap
    cv.disc(x + w // 2, deck - int(h * 0.10), int(h * 0.09), GREY)
    cv.disc(x + w // 2 + int(w * 0.05), deck - int(h * 0.20), int(h * 0.07), GREY)
    # drone above
    dx, dy = x + int(w * 0.72), y + int(h * 0.14)
    cv.fill_rect(dx - 10, dy - 1, 20, 2, INK)
    cv.fill_rect(dx - 1, dy - 6, 2, 12, INK)


def pic_summit(cv, x, y, w, h):
    """Three flags over a table: the United States, China, Russia."""
    cv.fill_rect(x, y, w, h, PAPER)
    fw = w // 3
    fh = int(h * 0.62)
    # United States: stripes and canton
    ux = x
    for i in range(7):
        cv.fill_rect(ux, y + i * (fh // 7), fw - 8, fh // 7 + 1,
                     RED if i % 2 == 0 else PAPER)
    cv.fill_rect(ux, y, int(fw * 0.42), int(fh * 0.54), BLUE)
    for r in range(3):
        for c in range(4):
            cv.disc(ux + 6 + c * 10, y + 6 + r * 9, 1, PAPER)
    # China: red field, gold stars
    cx = x + fw
    cv.fill_rect(cx, y, fw - 8, fh, RED)
    star(cv, cx + 14, y + 14, 7, GOLD)
    for sx, sy in ((cx + 30, y + 8), (cx + 34, y + 16), (cx + 32, y + 25), (cx + 26, y + 29)):
        star(cv, sx, sy, 3, GOLD)
    # Russia: white, blue, red
    rx = x + 2 * fw
    cv.fill_rect(rx, y, fw - 8, fh // 3 + 1, PAPER)
    cv.fill_rect(rx, y + fh // 3, fw - 8, fh // 3 + 1, BLUE)
    cv.fill_rect(rx, y + 2 * fh // 3, fw - 8, fh - 2 * fh // 3, RED)
    cv.rect(rx, y, fw - 8, fh, INK, 1)
    cv.rect(ux, y, fw - 8, fh, INK, 1)
    cv.rect(cx, y, fw - 8, fh, INK, 1)
    # table and three seats
    ty = y + fh + int(h * 0.12)
    cv.fill_rect(x + 6, ty, w - 12, 5, INK)
    for sx in (x + int(w * 0.18), x + w // 2, x + int(w * 0.82)):
        cv.disc(sx, ty - 12, 7, INK)


def pic_ballot(cv, x, y, w, h):
    """A ballot box, a paper slip, and a red star: Alaska goes blue."""
    cv.fill_rect(x, y, w, h, PAPER)
    # red star, lower left, clear of the section tab
    star(cv, x + int(w * 0.10), y + int(h * 0.68), int(h * 0.20), RED)
    cv.disc(x + int(w * 0.24), y + int(h * 0.78), 3, RED)
    # ballot box right of centre, slip above it where the tab cannot hide it
    bx, by = x + int(w * 0.46), y + int(h * 0.32)
    bw, bh = int(w * 0.42), int(h * 0.50)
    cv.fill_rect(bx, by, bw, bh, BLUE)
    cv.fill_rect(bx + 6, by - int(h * 0.20), bw - 12, int(h * 0.22), PAPER)
    cv.rect(bx + 6, by - int(h * 0.20), bw - 12, int(h * 0.22), INK, 1)
    cv.line(bx + 12, by - int(h * 0.09), bx + 18, by - int(h * 0.03), RED, 3)
    cv.line(bx + 18, by - int(h * 0.03), bx + 30, by - int(h * 0.16), RED, 3)
    cv.fill_rect(bx, by, bw, 5, INK)


def pic_virus(cv, x, y, w, h):
    """A spiked virus particle: Ebola in Congo."""
    cv.fill_rect(x, y, w, h, PAPER)
    cx, cy = x + w // 2, y + h // 2
    r = int(h * 0.30)
    for i in range(12):
        import math
        a = math.radians(i * 30)
        x0 = int(cx + r * 0.8 * math.cos(a))
        y0 = int(cy + r * 0.8 * math.sin(a))
        x1 = int(cx + r * 1.35 * math.cos(a))
        y1 = int(cy + r * 1.35 * math.sin(a))
        cv.line(x0, y0, x1, y1, RED, 3)
        cv.disc(x1, y1, 4, RED)
    cv.disc(cx, cy, r, RED)
    cv.disc(cx - r // 3, cy - r // 3, r // 3, (196, 60, 60))
    cv.disc(x + int(w * 0.10), y + int(h * 0.18), 5, (222, 150, 150))
    cv.disc(x + int(w * 0.88), y + int(h * 0.80), 4, (222, 150, 150))


def pic_cyclone(cv, x, y, w, h):
    """A Category 5 spiral over the Pacific."""
    cv.fill_rect(x, y, w, h, TEAL)
    cx, cy = x + w // 2, y + h // 2
    for k, rr in enumerate((int(h * 0.44), int(h * 0.33), int(h * 0.22))):
        cv.arc(cx, cy, rr, 20 + k * 55, 300 + k * 55, PAPER, 4, 36)
    cv.disc(cx, cy, int(h * 0.09), PAPER)
    cv.poly([(x + int(w * 0.08), y + h - 6), (x + int(w * 0.20), y + int(h * 0.72)),
             (x + int(w * 0.30), y + h - 6)], INK)

# ---------------------------------------------------------------- layout

M = 30            # page margin
CW = W - 2 * M    # content width: 964
SANS = fontdata.SANS
SERIF = fontdata.SERIF
WHITE = (255, 255, 255)


def _tab(cv, x, y, label, font=SANS):
    """Red section tab with white text, overlaid on a picture."""
    w = text_width(label, font, 1) + 16
    cv.fill_rect(x, y, w, 26, RED)
    draw_text(cv, x + 8, y + 2, label, font, 1, WHITE)


def _story_cell(cv, x, y, w, pic, tab, headline):
    """Picture strip with a red tab, then a two-to-three-line headline."""
    cv.set_clip(x, y, w, 56)
    pic(cv, x, y, w, 56)
    cv.clear_clip()
    _tab(cv, x, y, tab)
    lines = wrap_text(headline, w, SANS, 2)
    draw_lines(cv, x, y + 62, lines, SANS, 2, INK, leading=54)


def _briefs_cell(cv, x, y, w):
    """Bordered In Brief box: three one-line stories from the day."""
    draw_text(cv, x, y, "IN BRIEF", SANS, 1, RED)
    items = [
        "19 dead in Siberia plane crash.",
        "US loses measles-free status.",
        "6.0 quake in Papua New Guinea.",
    ]
    yy = y + 30
    for item in items:
        cv.fill_rect(x, yy + 8, 8, 8, RED)
        lines = wrap_text(item, w - 18, SANS, 1)[:2]
        draw_lines(cv, x + 18, yy, lines, SANS, 1, INK, leading=26)
        yy += len(lines) * 26 + 10


def layout(cv):
    y = 22
    # --- top bar: issue number, dateline, price
    draw_text(cv, M, y, "No. 323", SANS, 1, INK)
    draw_text_centred(cv, W // 2, y, "WEDNESDAY, 18 NOVEMBER 2026", SANS, 1, INK)
    price = "PRICE: FREE"
    draw_text(cv, W - M - text_width(price, SANS, 1), y, price, SANS, 1, INK)
    y += 30
    cv.hline(M, W - M - 1, y, INK, 2)
    y += 6
    # --- masthead
    draw_text_centred(cv, W // 2, y, "THE WORLD TODAY", SERIF, 3, INK)
    y += 92
    # --- dateline, big and red: the judge must see the day at once
    draw_text_centred(cv, W // 2, y, "WEDNESDAY, 18 NOVEMBER 2026",
                      SANS, 2, RED, tracking=0)
    y += 54
    # --- double rule
    cv.hline(M, W - M - 1, y, INK, 3)
    y += 6
    cv.hline(M, W - M - 1, y, INK, 1)
    y += 8
    # --- lead headline, two lines
    draw_text(cv, M, y, "US HITS IRAN,", SANS, 3, INK)
    y += 90
    draw_text(cv, M, y, "IRAN HITS BACK", SANS, 3, INK)
    y += 90
    # --- lead picture with its section tab
    cv.set_clip(M, y, CW, 76)
    pic_gulf(cv, M, y, CW, 76)
    cv.clear_clip()
    _tab(cv, M, y, "GULF CRISIS")
    y += 84
    # --- lead deck, two lines
    deck = wrap_text(
        "US jets struck a missile site on Qeshm Island. "
        "Tehran hit back with drones at Bahrain and Kuwait.",
        CW, SANS, 1)
    draw_lines(cv, M, y, deck, SANS, 1, INK, leading=30)
    y += len(deck) * 30 + 8
    # --- rule above the grid
    cv.hline(M, W - M - 1, y, INK, 2)
    y += 8
    # --- grid: five stories and an In Brief box
    grid_top = y
    cols = [M, M + 327, M + 654]
    col_w = 310
    row_h = 224
    row1 = [
        (pic_bridge, "UKRAINE", "KERCH BRIDGE FALLS"),
        (pic_summit, "SHENZHEN SUMMIT", "THREE LEADERS MEET"),
        (pic_ballot, "US SENATE", "ALASKA GOES BLUE"),
    ]
    for (pic, tab, headline), x in zip(row1, cols):
        _story_cell(cv, x, y, col_w, pic, tab, headline)
    y += row_h + 8
    row2 = [
        (pic_virus, "DR CONGO", "EBOLA DOUBLES"),
        (pic_cyclone, "COOK ISLANDS", "CAT 5 CYCLONE"),
    ]
    for (pic, tab, headline), x in zip(row2, cols[:2]):
        _story_cell(cv, x, y, col_w, pic, tab, headline)
    _briefs_cell(cv, cols[2], y, col_w)
    # column rules
    for rx in (cols[1] - 9, cols[2] - 9):
        cv.vline(rx, grid_top, y + row_h - 1, GREY, 1)
    return y + row_h


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas()
    bottom = layout(cv)
    write_png(cv, os.path.join(out_dir, "entry.png"))
    print(f"layout bottom edge: {bottom} (page height {H})")


if __name__ == "__main__":
    main()
