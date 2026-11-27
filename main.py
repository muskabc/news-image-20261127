# 27 Nov 2026 front page - code-drawn newspaper sheet.
# Pure stdlib: own 5x7 bitmap face, own raster helpers, own PNG packer.
import os
import struct
import zlib

SIDE = 1024

# palette for this edition
CREAM = (252, 248, 236)
COAL = (22, 22, 22)
CRIMSON = (190, 30, 45)
NAVY = (24, 62, 130)
SKYBLUE = (205, 228, 244)
VIOLET = (120, 70, 170)
AMBER = (245, 180, 20)
SNOW = (255, 255, 255)
SLATE = (130, 128, 120)
LEAF = (38, 140, 70)
TANGERINE = (240, 120, 30)
MIDNIGHT = (16, 48, 92)
AQUA = (20, 140, 140)

# 5x7 face, each glyph stored as seven 5-bit row masks (MSB = leftmost pixel)
GLYPHS = {
    'A': (14, 17, 17, 31, 17, 17, 17),
    'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (15, 16, 16, 16, 16, 16, 15),
    'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31),
    'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (15, 16, 16, 19, 17, 17, 14),
    'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),
    'J': (7, 2, 2, 2, 2, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13),
    'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),
    'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14),
    'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 27, 17),
    'X': (17, 10, 4, 4, 4, 10, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),
    'Z': (31, 1, 2, 4, 8, 16, 31),
    'a': (0, 0, 14, 1, 15, 17, 15),
    'b': (16, 16, 30, 17, 17, 17, 30),
    'c': (0, 0, 15, 16, 16, 16, 15),
    'd': (1, 1, 15, 17, 17, 17, 15),
    'e': (0, 0, 14, 17, 31, 16, 14),
    'f': (6, 4, 4, 30, 4, 4, 4),
    'g': (0, 15, 17, 17, 15, 1, 14),
    'h': (16, 16, 30, 17, 17, 17, 17),
    'i': (4, 0, 12, 4, 4, 4, 14),
    'j': (2, 0, 6, 2, 2, 2, 12),
    'k': (16, 16, 18, 20, 24, 20, 18),
    'l': (12, 4, 4, 4, 4, 4, 14),
    'm': (0, 0, 26, 21, 21, 21, 21),
    'n': (0, 0, 30, 17, 17, 17, 17),
    'o': (0, 0, 14, 17, 17, 17, 14),
    'p': (0, 0, 30, 17, 17, 30, 16),
    'q': (0, 0, 15, 17, 17, 15, 1),
    'r': (0, 0, 22, 25, 16, 16, 16),
    's': (0, 0, 15, 16, 14, 1, 30),
    't': (4, 4, 30, 4, 4, 4, 3),
    'u': (0, 0, 17, 17, 17, 19, 13),
    'v': (0, 0, 17, 17, 17, 10, 4),
    'w': (0, 0, 17, 21, 21, 21, 10),
    'x': (0, 0, 17, 10, 4, 10, 17),
    'y': (0, 0, 17, 17, 17, 15, 1),
    'z': (0, 0, 31, 2, 4, 8, 31),
    '0': (14, 17, 19, 21, 25, 17, 14),
    '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 2, 4, 8, 31),
    '3': (31, 2, 4, 2, 1, 17, 14),
    '4': (2, 6, 10, 18, 31, 2, 2),
    '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (6, 8, 16, 30, 17, 17, 14),
    '7': (31, 1, 2, 4, 4, 4, 4),
    '8': (14, 17, 17, 14, 17, 17, 14),
    '9': (14, 17, 17, 15, 1, 2, 12),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 12, 12),
    ',': (0, 0, 0, 0, 12, 4, 8),
    ':': (0, 12, 12, 0, 12, 12, 0),
    ';': (0, 12, 12, 0, 12, 4, 8),
    '!': (4, 4, 4, 4, 4, 0, 4),
    '?': (14, 17, 1, 2, 4, 0, 4),
    '-': (0, 0, 0, 14, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '"': (10, 10, 10, 0, 0, 0, 0),
    '(': (2, 4, 8, 8, 8, 4, 2),
    ')': (8, 4, 2, 2, 2, 4, 8),
    '%': (24, 25, 2, 4, 8, 19, 3),
    '/': (1, 2, 2, 4, 4, 8, 16),
    '&': (12, 18, 20, 8, 21, 18, 13),
    '$': (4, 15, 20, 14, 5, 30, 4),
    '+': (0, 4, 4, 31, 4, 4, 0),
    '=': (0, 0, 31, 0, 31, 0, 0),
    '*': (0, 4, 21, 14, 21, 4, 0),
    '#': (10, 10, 31, 10, 31, 10, 10),
    '[': (14, 8, 8, 8, 8, 8, 14),
    ']': (14, 2, 2, 2, 2, 2, 14),
    '_': (0, 0, 0, 0, 0, 0, 31),
    '<': (2, 4, 8, 16, 8, 4, 2),
    '>': (8, 4, 2, 1, 2, 4, 8),
}


class Sheet:
    """Tiny RGB canvas kept as a flat bytearray."""
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def dot(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            k = (y * self.w + x) * 3
            self.buf[k] = rgb[0]
            self.buf[k + 1] = rgb[1]
            self.buf[k + 2] = rgb[2]

    def box(self, x, y, w, h, rgb):
        for yy in range(y, y + h):
            if yy < 0 or yy >= self.h:
                continue
            base = yy * self.w * 3
            for xx in range(x, x + w):
                if 0 <= xx < self.w:
                    k = base + xx * 3
                    self.buf[k] = rgb[0]
                    self.buf[k + 1] = rgb[1]
                    self.buf[k + 2] = rgb[2]

    def frame(self, x, y, w, h, rgb, t=1):
        self.box(x, y, w, t, rgb)
        self.box(x, y + h - t, w, t, rgb)
        self.box(x, y, t, h, rgb)
        self.box(x + w - t, y, t, h, rgb)

    def disc(self, cx, cy, r, rgb):
        rr = r * r
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            for xx in range(cx - r, cx + r + 1):
                dx = xx - cx
                if dx * dx + dy * dy <= rr:
                    self.dot(xx, yy, rgb)

    def seg(self, x0, y0, x1, y1, rgb):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.dot(x0 + (x1 - x0) * i // n, y0 + (y1 - y0) * i // n, rgb)

    def tri(self, ax, ay, bx, by, cx, cy, rgb):
        # barycentric fill
        xlo = min(ax, bx, cx)
        xhi = max(ax, bx, cx)
        ylo = min(ay, by, cy)
        yhi = max(ay, by, cy)
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if den == 0:
            return
        for yy in range(ylo, yhi + 1):
            for xx in range(xlo, xhi + 1):
                w1 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / den
                w2 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / den
                w3 = 1.0 - w1 - w2
                if w1 >= 0 and w2 >= 0 and w3 >= 0:
                    self.dot(xx, yy, rgb)


STEP = 6  # glyph cell advance in unit pixels (5 + 1 gap)


def measure(s, scale):
    return len(s) * STEP * scale


def stamp(sheet, s, x, y, scale, rgb):
    pen = x
    blank = GLYPHS[' ']
    for ch in s:
        rows = GLYPHS.get(ch, blank)
        for ri in range(7):
            bits = rows[ri]
            for ci in range(5):
                if bits & (1 << (4 - ci)):
                    sheet.box(pen + ci * scale, y + ri * scale, scale, scale, rgb)
        pen += STEP * scale


def stamp_mid(sheet, s, cx, y, scale, rgb):
    stamp(sheet, s, cx - measure(s, scale) // 2, y, scale, rgb)


def break_lines(s, limit_px, scale):
    out = []
    cur = ""
    for word in s.split(" "):
        cand = word if cur == "" else cur + " " + word
        if measure(cand, scale) <= limit_px or cur == "":
            cur = cand
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def body(sheet, s, x, y, limit_px, scale, rgb, lead):
    for ln in break_lines(s, limit_px, scale):
        stamp(sheet, ln, x, y, scale, rgb)
        y += lead
    return y


def kicker(sheet, num, label, x, y):
    sheet.box(x, y, 22, 22, CRIMSON)
    stamp(sheet, num, x + 7, y + 4, 2, SNOW)
    stamp(sheet, label, x + 30, y + 4, 2, CRIMSON)


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode(sheet):
    lines = bytearray()
    stride = sheet.w * 3
    for yy in range(sheet.h):
        lines.append(0)
        a = yy * stride
        lines.extend(sheet.buf[a:a + stride])
    header = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(lines), 9)) + chunk(b"IEND", b"")


def render():
    pg = Sheet(SIDE, SIDE, CREAM)
    # double border
    pg.frame(14, 14, 996, 996, COAL, 2)
    pg.frame(20, 20, 984, 984, COAL, 1)

    # masthead block
    stamp_mid(pg, "THE WORLD TODAY", 512, 36, 7, COAL)
    pg.box(32, 94, 960, 2, COAL)
    stamp_mid(pg, "FRIDAY 27 NOVEMBER 2026", 512, 102, 4, CRIMSON)
    pg.box(32, 136, 960, 1, COAL)
    pg.box(32, 139, 960, 2, COAL)
    stamp_mid(pg, "OVERNIGHT NEWS AND TODAYS EVENTS WORLDWIDE", 512, 150, 2, COAL)
    pg.box(32, 170, 960, 1, SLATE)

    # --- Story 1: Kuwait drone strike (lead) ---
    kicker(pg, "1", "SECURITY - KUWAIT", 50, 190)
    stamp(pg, "TWO ITALIANS KILLED", 50, 218, 4, COAL)
    stamp(pg, "IN DRONE STRIKE", 50, 252, 4, COAL)
    body(pg,
         "Two Italian defence technicians died overnight when drones struck an air-defence station in Kuwait. Italy and Kuwait blame Iran, which denies the attack. Two more people were hurt.",
         50, 292, 596, 2, COAL, 18)
    pg.box(50, 388, 596, 1, SLATE)
    stamp(pg, "KUWAIT - REUTERS", 50, 394, 2, COAL)

    # radar picture panel
    pg.box(678, 186, 296, 214, SKYBLUE)
    pg.frame(678, 186, 296, 214, COAL, 1)
    stamp(pg, "KUWAIT", 690, 196, 2, NAVY)
    pg.box(698, 340, 256, 8, MIDNIGHT)
    pg.tri(760, 340, 828, 270, 896, 340, MIDNIGHT)
    pg.disc(828, 270, 15, SNOW)
    pg.disc(828, 270, 9, SKYBLUE)
    pg.seg(828, 270, 894, 226, CRIMSON)
    pg.disc(902, 222, 9, CRIMSON)
    pg.disc(902, 222, 4, SNOW)
    pg.box(714, 218, 42, 10, COAL)
    pg.box(728, 206, 14, 12, COAL)
    pg.disc(710, 223, 6, SLATE)
    pg.disc(760, 223, 6, SLATE)
    pg.box(678, 392, 296, 3, COAL)

    pg.box(32, 424, 960, 2, COAL)

    # --- Story 2: Congo Ebola ---
    kicker(pg, "2", "HEALTH - CONGO", 50, 440)
    stamp(pg, "EBOLA PASSES 12,000", 50, 468, 3, COAL)
    stamp(pg, "CASES IN THE EAST", 50, 494, 3, COAL)
    body(pg,
         "Eastern Congo has passed 12,000 confirmed Ebola cases, with nearly half fatal. The Bundibugyo outbreak is the fastest-growing on record, has no approved vaccine, and fighting slows responders.",
         50, 524, 432, 2, COAL, 18)
    pg.disc(112, 670, 21, VIOLET)
    pg.disc(105, 663, 5, SNOW)
    pg.disc(121, 677, 4, SNOW)
    pg.disc(188, 670, 14, CRIMSON)
    pg.disc(244, 670, 9, TANGERINE)
    stamp(pg, "12,021 CASES", 280, 661, 2, COAL)

    # --- Story 3: UK migration ---
    kicker(pg, "3", "BRITAIN - MIGRATION", 542, 440)
    stamp(pg, "NET MIGRATION", 542, 468, 3, COAL)
    stamp(pg, "DOWN TO 77,000", 542, 494, 3, COAL)
    body(pg,
         "UK net migration fell to 77,000 in the year to June, down from 204,000, the lowest since 1997 outside the pandemic, ONS figures show.",
         542, 524, 432, 2, COAL, 18)
    stamp_mid(pg, "204,000", 640, 598, 2, COAL)
    stamp_mid(pg, "77,000", 854, 598, 2, CRIMSON)
    pg.box(613, 618, 54, 55, NAVY)
    pg.box(827, 643, 54, 30, CRIMSON)
    pg.seg(667, 633, 827, 633, COAL)
    pg.tri(827, 628, 827, 638, 843, 633, COAL)
    pg.box(542, 673, 432, 2, COAL)
    stamp(pg, "LAST YEAR    THIS YEAR", 590, 680, 2, COAL)

    pg.box(512, 436, 1, 258, SLATE)
    pg.box(32, 706, 960, 2, COAL)

    # --- Story 4: chess in Geneva ---
    kicker(pg, "4", "CHESS - GENEVA", 50, 722)
    stamp(pg, "LEVEL AT 1.5-1.5", 50, 750, 3, COAL)
    stamp(pg, "AFTER GAME 3", 50, 776, 3, COAL)
    body(pg,
         "Gukesh of India and Sindarov of Uzbekistan drew Game 3 in 60 moves in Geneva. Friday is the first rest day; Game 4 follows Saturday with Gukesh as White.",
         50, 806, 432, 2, COAL, 18)
    # mini board: 8 wide, 4 tall, green/white squares
    ox, oy, sq = 50, 900, 14
    for rr in range(4):
        for cc in range(8):
            tone = LEAF if (rr + cc) % 2 == 0 else SNOW
            pg.box(ox + cc * sq, oy + rr * sq, sq, sq, tone)
    pg.frame(ox - 3, oy - 3, 8 * sq + 6, 4 * sq + 6, MIDNIGHT, 3)
    for cc in range(8):
        px = ox + cc * sq + 7
        pg.disc(px, oy + 7, 4, COAL)
        pg.disc(px, oy + 3 * sq + 7, 5, COAL)
        pg.disc(px, oy + 3 * sq + 7, 4, SNOW)
    for kx, ky, body_c in ((ox + 3 * sq + 7, oy + 7, COAL), (ox + 4 * sq + 7, oy + 3 * sq + 7, SNOW)):
        pg.box(kx - 2, ky - 6, 5, 9, body_c)
        pg.disc(kx, ky - 7, 3, body_c)
        if body_c == SNOW:
            pg.frame(kx - 2, ky - 6, 5, 9, COAL, 1)
    stamp(pg, "REST DAY TODAY", 184, 914, 2, CRIMSON)
    stamp(pg, "GAME 4 SATURDAY", 184, 934, 2, COAL)

    # --- Story 5: Black Friday ---
    kicker(pg, "5", "USA - BLACK FRIDAY", 542, 722)
    stamp(pg, "BLACK FRIDAY", 542, 750, 3, COAL)
    stamp(pg, "SHOPPING TODAY", 542, 776, 3, COAL)
    body(pg,
         "Stores open early across the US for Black Friday, the day after Thanksgiving, with one-day travel flash deals next to shop sales.",
         542, 806, 432, 2, COAL, 18)
    pg.box(562, 908, 90, 48, TANGERINE)
    pg.frame(562, 908, 90, 48, COAL, 1)
    pg.box(590, 894, 34, 16, COAL)
    stamp_mid(pg, "SALE", 607, 924, 2, SNOW)
    pg.disc(742, 932, 21, AMBER)
    pg.frame(720, 910, 44, 44, COAL, 2)
    stamp_mid(pg, "%", 742, 924, 2, COAL)
    stamp(pg, "TODAY ONLY", 792, 922, 2, CRIMSON)

    # footer
    pg.box(32, 962, 960, 1, COAL)
    stamp_mid(pg, "Sources: Reuters, AP, ONS via Reuters, Chess.com.", 512, 970, 2, COAL)
    stamp_mid(pg, "Overnight reports and events of Friday 27 November 2026.", 512, 988, 2, COAL)
    return pg


def main():
    sheet = render()
    dest = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "entry.png"), "wb") as fh:
        fh.write(encode(sheet))


if __name__ == "__main__":
    main()
