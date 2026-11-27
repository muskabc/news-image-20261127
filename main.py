# Friday front page for 27 November 2026, drawn with code only.
# Standard library Python paints a 1024 square newspaper image:
# block letters from the string font below, flat shapes for the
# pictures, and a deterministic PNG encoder, so two runs agree.
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (250, 246, 232)
INK = (26, 26, 26)
RED = (178, 34, 34)
BLUE = (28, 78, 150)
SKY = (198, 224, 242)
PURPLE = (104, 62, 160)
YELLOW = (246, 198, 8)
WHITE = (255, 255, 255)
GREY = (124, 122, 114)
GREEN = (44, 128, 58)
ORANGE = (234, 124, 34)
DARKBLUE = (18, 52, 96)
TEAL = (16, 126, 126)

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
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
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": (".##..", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".#.##"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "/": ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".#.##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
}

pixels = bytearray(W * H * 3)


def set_px(x, y, colour):
    if 0 <= x < W and 0 <= y < H:
        pos = (y * W + x) * 3
        pixels[pos] = colour[0]
        pixels[pos + 1] = colour[1]
        pixels[pos + 2] = colour[2]


def rect(x, y, w, h, colour):
    for row in range(y, y + h):
        for col in range(x, x + w):
            set_px(col, row, colour)


def border(x, y, w, h, colour, thick=1):
    rect(x, y, w, thick, colour)
    rect(x, y + h - thick, w, thick, colour)
    rect(x, y, thick, h, colour)
    rect(x + w - thick, y, thick, h, colour)


def hline(x, y, length, colour, thick=1):
    rect(x, y, length, thick, colour)


def vline(x, y, length, colour, thick=1):
    rect(x, y, thick, length, colour)


def draw_line(x0, y0, x1, y1, colour):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        set_px(x0 + (x1 - x0) * i // steps, y0 + (y1 - y0) * i // steps, colour)


def circle(cx, cy, radius, colour):
    for dy in range(-radius, radius + 1):
        half = int((radius * radius - dy * dy) ** 0.5)
        for dx in range(-half, half + 1):
            set_px(cx + dx, cy + dy, colour)


def tri(x0, y0, x1, y1, x2, y2, colour):
    lo_y = min(y0, y1, y2)
    hi_y = max(y0, y1, y2)
    edges = ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0))
    for yy in range(lo_y, hi_y + 1):
        cuts = []
        for ax, ay, bx, by in edges:
            if (ay <= yy < by) or (by <= yy < ay):
                cuts.append(ax + (yy - ay) * (bx - ax) / (by - ay))
        if len(cuts) >= 2:
            left = int(min(cuts) + 0.999)
            right = int(max(cuts))
            for xx in range(left, right + 1):
                set_px(xx, yy, colour)


ADV = 6


def text_w(text, scale):
    return len(text) * ADV * scale


def put_text(text, x, y, scale, colour):
    cx = x
    for ch in text:
        rows = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = rows[r]
            for c in range(5):
                if row[c] == "#":
                    rect(cx + c * scale, y + r * scale, scale, scale, colour)
        cx += ADV * scale


def put_center(text, centre, y, scale, colour):
    put_text(text, centre - text_w(text, scale) // 2, y, scale, colour)


def wrap(text, max_w, scale):
    lines = []
    cur = ""
    for word in text.split(" "):
        trial = word if cur == "" else cur + " " + word
        if text_w(trial, scale) <= max_w or cur == "":
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur != "":
        lines.append(cur)
    return lines


def para(text, x, y, max_w, scale, colour, leading):
    for ln in wrap(text, max_w, scale):
        put_text(ln, x, y, scale, colour)
        y += leading
    return y


def tag(num, label, x, y):
    rect(x, y, 20, 20, RED)
    put_text(num, x + 7, y + 3, 2, WHITE)
    put_text(label, x + 28, y + 3, 2, RED)


# Page ground with a double rule border.
rect(0, 0, W, H, PAPER)
border(12, 12, 1000, 1000, INK, 2)
border(18, 18, 988, 988, INK, 1)

# Masthead and date line.
put_center("THE WORLD TODAY", 512, 34, 7, INK)
hline(30, 92, 964, INK, 2)
put_center("FRIDAY 27 NOVEMBER 2026", 512, 100, 4, RED)
hline(30, 134, 964, INK, 1)
hline(30, 137, 964, INK, 2)
put_center("OVERNIGHT NEWS AND TODAYS EVENTS WORLDWIDE", 512, 148, 2, INK)
hline(30, 168, 964, GREY, 1)

# Lead story: Kuwait air-defence station attack.
tag("1", "SECURITY - KUWAIT", 48, 188)
put_text("TWO ITALIANS KILLED", 48, 214, 4, INK)
put_text("IN DRONE STRIKE", 48, 248, 4, INK)
para(
    "Two Rheinmetall Italia technicians died when drones hit an air-defence station in Kuwait overnight. Italy and Kuwait blame Iran; Tehran denies any attack. Two others were injured.",
    48, 288, 600, 2, INK, 18,
)
hline(48, 386, 600, GREY, 1)
put_text("DUBAI AND ROME - REUTERS", 48, 392, 2, INK)

# Radar and drone panel beside the lead.
rect(680, 184, 296, 216, SKY)
border(680, 184, 296, 216, INK, 1)
put_text("KUWAIT", 692, 194, 2, BLUE)
rect(700, 340, 256, 8, DARKBLUE)
tri(760, 340, 830, 268, 900, 340, DARKBLUE)
circle(830, 268, 16, WHITE)
circle(830, 268, 10, SKY)
draw_line(830, 268, 898, 222, RED)
circle(906, 218, 10, RED)
circle(906, 218, 5, WHITE)
rect(716, 216, 44, 10, INK)
rect(730, 204, 16, 12, INK)
circle(712, 221, 7, GREY)
circle(764, 221, 7, GREY)
hline(680, 392, 296, INK, 3)

hline(30, 424, 964, INK, 2)

# Second story: Congo Ebola milestone.
tag("2", "HEALTH - CONGO", 48, 440)
put_text("EBOLA TOPS 12,000", 48, 468, 3, INK)
put_text("CASES IN EAST", 48, 494, 3, INK)
para(
    "Eastern Congo has passed 12,000 confirmed Ebola cases, nearly half fatal. It is the fastest-growing outbreak on record, with no approved vaccine, as fighting hampers responders.",
    48, 522, 436, 2, INK, 18,
)
circle(110, 668, 22, PURPLE)
circle(103, 661, 5, WHITE)
circle(119, 675, 4, WHITE)
circle(188, 668, 15, RED)
circle(246, 668, 10, ORANGE)
put_text("12,021 CASES", 282, 659, 2, INK)

# Third story: UK migration figures.
tag("3", "BRITAIN - MIGRATION", 540, 440)
put_text("NET MIGRATION", 540, 468, 3, INK)
put_text("FALLS TO 77,000", 540, 494, 3, INK)
para(
    "UK net migration fell to 77,000 in the year to June, down from 204,000 and the lowest since 1997 outside the pandemic, official figures show.",
    540, 522, 436, 2, INK, 18,
)
put_center("204,000", 640, 598, 2, INK)
put_center("77,000", 856, 598, 2, RED)
rect(613, 618, 54, 55, BLUE)
rect(829, 643, 54, 30, RED)
draw_line(667, 633, 829, 633, INK)
tri(829, 628, 829, 638, 845, 633, INK)
hline(540, 673, 436, INK, 2)
put_text("LAST YEAR    THIS YEAR", 588, 680, 2, INK)

vline(512, 436, 260, GREY, 1)
hline(30, 706, 964, INK, 2)

# Fourth story: world chess championship in Geneva.
tag("4", "CHESS - GENEVA", 48, 722)
put_text("LEVEL AT 1.5-1.5", 48, 750, 3, INK)
put_text("AFTER GAME 3", 48, 776, 3, INK)
para(
    "Gukesh and Sindarov drew Game 3 in 60 moves in Geneva. Today is the first rest day; Game 4 is on Saturday with Gukesh to play White.",
    48, 804, 436, 2, INK, 18,
)
# Square-celled half board in green and cream, with pawn rows and
# two kings, so the graphic reads at once as a chess position.
bx = 48
by = 890
sq = 14
for rr in range(4):
    for cc in range(8):
        tone = GREEN if (rr + cc) % 2 == 0 else WHITE
        rect(bx + cc * sq, by + rr * sq, sq, sq, tone)
border(bx - 3, by - 3, 8 * sq + 6, 4 * sq + 6, DARKBLUE, 3)
for cc in range(8):
    px = bx + cc * sq + 7
    circle(px, by + 7, 4, INK)
    circle(px, by + 3 * sq + 7, 5, INK)
    circle(px, by + 3 * sq + 7, 4, WHITE)
for kx, ky, body in ((bx + 3 * sq + 7, by + 7, INK), (bx + 4 * sq + 7, by + 3 * sq + 7, WHITE)):
    rect(kx - 2, ky - 6, 5, 9, body)
    circle(kx, ky - 7, 3, body)
    if body == WHITE:
        border(kx - 2, ky - 6, 5, 9, INK, 1)
put_text("REST DAY TODAY", 182, 906, 2, RED)
put_text("GAME 4 SATURDAY", 182, 926, 2, INK)

# Fifth story: Black Friday shopping day.
tag("5", "USA - BLACK FRIDAY", 540, 722)
put_text("BLACK FRIDAY", 540, 750, 3, INK)
put_text("SHOPPING TODAY", 540, 776, 3, INK)
para(
    "Shops open early across the US for Black Friday, the day after Thanksgiving, with one-day travel flash deals alongside store sales.",
    540, 804, 436, 2, INK, 18,
)
rect(560, 906, 90, 48, ORANGE)
border(560, 906, 90, 48, INK, 1)
rect(588, 892, 34, 16, INK)
put_center("SALE", 605, 922, 2, WHITE)
circle(740, 930, 22, YELLOW)
border(718, 908, 44, 44, INK, 2)
put_center("%", 740, 922, 2, INK)
put_text("TODAY ONLY", 790, 920, 2, RED)

# Footer with sources and date.
hline(30, 962, 964, INK, 1)
footer_lines = (
    "Sources: Reuters, AP via NPR, ONS via Reuters, Chess.com.",
    "Overnight reports and events of Friday 27 November 2026.",
)
for idx, txt in enumerate(footer_lines):
    put_center(txt, W // 2, 970 + idx * 18, 2, INK)


def make_chunk(kind, payload):
    size = struct.pack(">I", len(payload))
    check = struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return size + kind + payload + check


def build_png():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        start = yy * W * 3
        raw.extend(pixels[start:start + W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(b"IHDR", ihdr)
        + make_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + make_chunk(b"IEND", b"")
    )


out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "entry.png"), "wb") as out_file:
    out_file.write(build_png())
