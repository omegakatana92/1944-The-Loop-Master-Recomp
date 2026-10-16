#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Draws the port's icon, tools/release/1944.png (256x256): the fighter climbing out of a loop in
its own smoke trail, over a night sky, with the game's year. Everything here is arithmetic — no
artwork from the game is used or copied, so the releases ship none. Rebuild it with:

    python3 tools/release/make-icon.py

Each shape is rasterised with one bit per pixel at SS-times the final size, then averaged down, which
is what gives the edges their smoothness.
"""

import math
import os
import struct
import zlib

W = H = 256
SS = 3          # sub-pixels per pixel, per axis
SW = W * SS     # the size the shapes are drawn at

# --- palette -------------------------------------------------------------------------------------
SKY_TOP = (10, 18, 40)
SKY_BOTTOM = (46, 82, 130)
GLOW = (70, 116, 168)          # a soft light behind the loop
CLOUD = (58, 92, 138)
INK = (7, 12, 26)              # the outlines
TRAIL = (226, 236, 248)
PLANE = (250, 205, 105)
YEAR = (250, 205, 105)

# --- bit-row masks (one int per row: bit x is set if that sub-pixel is filled) --------------------

def mask_from_spans(rows):
    """Build a mask from {y: [(x0, x1), ...]} half-open spans, in final-pixel coordinates."""
    m = [0] * SW
    for y, spans in rows.items():
        ys = range(max(0, y * SS), min(SW, (y + 1) * SS))
        bits = 0
        for x0, x1 in spans:
            xa, xb = max(0, int(x0 * SS)), min(SW, int(x1 * SS))
            if xb > xa:
                bits |= ((1 << (xb - xa)) - 1) << xa
        for yy in ys:
            m[yy] |= bits
    return m


def polygon(points):
    """A filled polygon, as a mask."""
    spans = {}
    ys = [p[1] for p in points]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        yc = y + 0.5
        xs = []
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        spans[y] = [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
    return mask_from_spans(spans)


def ellipse(cx, cy, rx, ry):
    """A filled ellipse, as a mask."""
    spans = {}
    for y in range(int(cy - ry), int(cy + ry) + 1):
        dy = (y + 0.5 - cy) / ry
        if abs(dy) >= 1:
            continue
        dx = rx * (1 - dy * dy) ** 0.5
        spans[y] = [(cx - dx, cx + dx)]
    return mask_from_spans(spans)


def union(*masks):
    out = [0] * SW
    for m in masks:
        for y in range(SW):
            out[y] |= m[y]
    return out


def disc(mask, cx, cy, r):
    """OR a filled circle of radius r (sub-pixels, y down) into a mask."""
    for y in range(max(0, int(cy - r)), min(SW, int(cy + r) + 1)):
        dy = y + 0.5 - cy
        if abs(dy) > r:
            continue
        dx = (r * r - dy * dy) ** 0.5
        xa, xb = max(0, int(cx - dx)), min(SW - 1, int(cx + dx))
        if xb >= xa:
            mask[y] |= ((1 << (xb - xa + 1)) - 1) << xa
    return mask


def stroke(points, width):
    """A thick line through the points, rounded at both ends (all in final-pixel coordinates)."""
    mask = [0] * SW
    r = width * SS / 2.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = int(max(1.0, math.hypot(x1 - x0, y1 - y0) * SS))
        for i in range(steps + 1):
            t = i / float(steps)
            disc(mask, (x0 + (x1 - x0) * t) * SS, (y0 + (y1 - y0) * t) * SS, r)
    return mask


def spread(mask, r):
    """Grow a mask by r sub-pixels (a square brush: indistinguishable from a round one here)."""
    out = mask[:]
    for dy in range(-r, r + 1):
        for y in range(SW):
            sy = y + dy
            if 0 <= sy < SW:
                out[y] |= mask[sy]
    for y in range(SW):
        row = out[y]
        acc = 0
        for dx in range(-r, r + 1):
            acc |= row << dx if dx > 0 else row >> -dx
        out[y] = acc & ((1 << SW) - 1)
    return out


def minus(a, b):
    return [a[y] & ~b[y] for y in range(SW)]


def coverage(mask):
    """How much of each final pixel is filled, 0..1."""
    cov = [[0.0] * W for _ in range(H)]
    group = (1 << SS) - 1
    for y in range(H):
        rows = mask[y * SS:(y + 1) * SS]
        for x in range(W):
            sh = x * SS
            n = 0
            for row in rows:
                n += bin((row >> sh) & group).count("1")
            cov[y][x] = n / float(SS * SS)
    return cov


# --- the shapes -----------------------------------------------------------------------------------

FONT = {
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    "9": [".XXX.", "X...X", "X...X", ".XXXX", "....X", "...X.", ".XX.."],
    "4": ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
}


def year_mask(scale=8, x0=36, y0=12):
    """The four digits of the year, drawn from the 5x7 font above."""
    spans = {}
    x = x0
    for ch in "1944":
        for r in range(7):
            for c in range(5):
                if FONT[ch][r][c] != "X":
                    continue
                for yy in range(y0 + r * scale, y0 + (r + 1) * scale):
                    spans.setdefault(yy, []).append((x + c * scale, x + (c + 1) * scale))
        x += 6 * scale
    return mask_from_spans(spans)


def loop_trail():
    """The smoke: straight in from the bottom, a full loop, then up and away through it."""
    cx, cy, r = 128.0, 206.0, 36.0
    points = [(128.0, 250.0), (cx, cy + r)]
    for i in range(0, 361, 3):
        a = math.radians(-90.0 + i)              # start at the bottom, loop the loop
        points.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    points += [(cx, cy + r), (128.0, 156.0)]     # back up through the loop, into the fighter
    return stroke(points, 6)


def plane_mask():
    """A swept-wing fighter seen from above, nose up: one outline, which is what reads at icon
    size — a pointed nose, wings sweeping back to a point on each side, and a flat tail."""
    return polygon([(128, 80), (140, 118), (188, 152), (188, 160), (140, 150), (140, 162),
                    (116, 162), (116, 150), (68, 160), (68, 152), (116, 118)])


def background():
    """The sky: a vertical gradient, a light behind the loop, and a few clouds."""
    img = [[[0.0] * 3 for _ in range(W)] for _ in range(H)]
    for y in range(H):
        t = y / float(H - 1)
        base = [SKY_TOP[i] + (SKY_BOTTOM[i] - SKY_TOP[i]) * t for i in range(3)]
        for x in range(W):
            glow = max(0.0, 1.0 - (((x - 128) ** 2 + (y - 186) ** 2) ** 0.5) / 150.0)
            img[y][x] = [base[i] + (GLOW[i] - base[i]) * glow * 0.5 for i in range(3)]
    cloud = union(ellipse(56, 100, 52, 7), ellipse(200, 128, 58, 8), ellipse(124, 62, 64, 6))
    cov = coverage(cloud)
    for y in range(H):
        for x in range(W):
            c = cov[y][x] * 0.16
            if c:
                img[y][x] = [img[y][x][i] + (CLOUD[i] - img[y][x][i]) * c for i in range(3)]
    return img


def over(img, cov, colour):
    for y in range(H):
        for x in range(W):
            a = cov[y][x]
            if a:
                px = img[y][x]
                img[y][x] = [px[i] + (colour[i] - px[i]) * a for i in range(3)]


def main():
    trail = loop_trail()
    plane = plane_mask()
    year = year_mask()
    # The outlines: what the shape grew over, minus the shape itself.
    plane_ring = minus(spread(plane, 7), spread(plane, 3))
    year_ring = minus(spread(year, 7), spread(year, 3))

    img = background()
    over(img, coverage(trail), TRAIL)
    over(img, coverage(plane_ring), INK)
    over(img, coverage(plane), PLANE)
    over(img, coverage(year_ring), INK)
    over(img, coverage(year), YEAR)

    rows = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            for i in range(3):
                row.append(max(0, min(255, int(img[y][x][i] + 0.5))))
        rows.append(row)

    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1944.png")
    with open(out, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (out, len(png)))


if __name__ == "__main__":
    main()
