from PIL import Image
import os

# الصورة الأصلية
IMAGE = "bot_moroccan_uno_pack.png"

# مجلد الإخراج
OUT = "assets/cards"

os.makedirs(OUT, exist_ok=True)

img = Image.open(IMAGE)

# المقاسات تقريبية للصورة اللي عندك
CARD_W = 90
CARD_H = 130

# أسماء الألوان
colors = [
    "red",
    "green",
    "blue",
    "yellow"
]

# مواقع أول بطاقة فكل سطر
START_X = 60
START_Y = [
    175,  # red
    315,  # green
    455,  # blue
    595   # yellow
]

STEP_X = 115

# استخراج الأرقام
for row, color in enumerate(colors):

    y = START_Y[row]

    for n in range(10):

        x = START_X + STEP_X * n

        card = img.crop(
            (
                x,
                y,
                x + CARD_W,
                y + CARD_H
            )
        )

        card.save(
            f"{OUT}/{color}_{n}.png"
        )

# Action cards
ACTION_Y = 735

action_positions = [
    ("red_skip", 60),
    ("red_reverse", 175),
    ("red_draw2", 290),

    ("green_skip", 405),
    ("green_reverse", 520),
    ("green_draw2", 635),

    ("blue_skip", 750),
    ("blue_reverse", 865),
    ("blue_draw2", 980),

    ("yellow_skip", 1095),
    ("yellow_reverse", 1210),
    ("yellow_draw2", 1325),
]

for name, x in action_positions:

    card = img.crop(
        (
            x,
            ACTION_Y,
            x + CARD_W,
            ACTION_Y + CARD_H
        )
    )

    card.save(
        f"{OUT}/{name}.png"
    )

# Wild cards
WILD_Y = 930

wild_positions = [
    ("wild", 50),
    ("wild4", 520),
]

for name, x in wild_positions:

    card = img.crop(
        (
            x,
            WILD_Y,
            x + CARD_W,
            WILD_Y + CARD_H
        )
    )

    card.save(
        f"{OUT}/{name}.png"
    )

# Card back
BACK_X = 1120
BACK_Y = 915

card = img.crop(
    (
        BACK_X,
        BACK_Y,
        BACK_X + CARD_W,
        BACK_Y + CARD_H
    )
)

card.save(
    f"{OUT}/back.png"
)

print("DONE")