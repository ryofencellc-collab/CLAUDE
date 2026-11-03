"""Draws the Village of Lights icon (512x512) and thumbnail (1920x1080) for the Creator Hub."""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parent
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sky(w, h):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(25 + 40 * t), int(10 + 20 * t), int(60 + 30 * t)))
    return img


def fireworks(img, n, rng, scale):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    colors = [(255, 170, 0), (0, 200, 210), (255, 210, 60), (255, 120, 200), (200, 160, 255)]
    for _ in range(n):
        cx, cy = rng.uniform(0.1, 0.9) * img.width, rng.uniform(0.05, 0.45) * img.height
        c = rng.choice(colors)
        r = rng.uniform(40, 110) * scale
        for k in range(28):
            a = k / 28 * math.tau
            x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
            d.line([(cx + math.cos(a) * r * 0.3, cy + math.sin(a) * r * 0.3), (x, y)], fill=c + (230,), width=max(2, int(3 * scale)))
            d.ellipse([x - 4 * scale, y - 4 * scale, x + 4 * scale, y + 4 * scale], fill=c + (255,))
    img.paste(glow.filter(ImageFilter.GaussianBlur(6 * scale)), (0, 0), glow.filter(ImageFilter.GaussianBlur(6 * scale)))
    img.paste(glow, (0, 0), glow)


def diya(img, cx, cy, s):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - 90 * s, cy - 120 * s, cx + 90 * s, cy + 60 * s], fill=(255, 160, 40, 90))  # glow
    d.pieslice([cx - 70 * s, cy - 40 * s, cx + 70 * s, cy + 50 * s], 0, 180, fill=(190, 90, 35, 255))  # bowl
    d.rectangle([cx - 70 * s, cy + 2 * s, cx + 70 * s, cy + 8 * s], fill=(235, 180, 60, 255))  # rim
    d.polygon([(cx, cy - 75 * s), (cx - 16 * s, cy - 10 * s), (cx + 16 * s, cy - 10 * s)], fill=(255, 200, 60, 255))  # flame
    d.polygon([(cx, cy - 50 * s), (cx - 7 * s, cy - 12 * s), (cx + 7 * s, cy - 12 * s)], fill=(255, 250, 220, 255))
    blurred = layer.filter(ImageFilter.GaussianBlur(14 * s))
    img.paste(blurred, (0, 0), blurred)
    img.paste(layer, (0, 0), layer)


def title(img, text, size, y):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(BOLD, size)
    w = d.textbbox((0, 0), text, font=f)[2]
    x = (img.width - w) / 2
    for dx in range(-4, 5, 2):
        for dy in range(-4, 5, 2):
            d.text((x + dx, y + dy), text, font=f, fill=(60, 20, 0))
    d.text((x, y), text, font=f, fill=(255, 205, 70))


def main():
    rng = random.Random(8)
    icon = sky(512, 512)
    fireworks(icon, 3, rng, 0.7)
    diya(icon, 256, 330, 1.6)
    title(icon, "DIWALI", 78, 400)
    icon.save(OUT / "icon_512.png")

    thumb = sky(1920, 1080)
    fireworks(thumb, 8, rng, 1.4)
    for i, x in enumerate(range(240, 1920, 360)):
        diya(thumb, x, 850 + (i % 2) * 40, 1.2)
    title(thumb, "VILLAGE OF LIGHTS", 150, 420)
    title(thumb, "Light the village · Fireworks · Ultra-rare finds", 56, 610)
    thumb.save(OUT / "thumbnail_1920x1080.png")


if __name__ == "__main__":
    main()
