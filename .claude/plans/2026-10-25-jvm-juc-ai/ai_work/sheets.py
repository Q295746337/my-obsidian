# -*- coding: utf-8 -*-
import os, math
from PIL import Image, ImageDraw, ImageFont
BASE = r"D:\Java\Obisidian笔记\.claude\plans\2026-10-25-jvm-juc-ai\ai_work\images"
OUT = r"D:\Java\Obisidian笔记\.claude\plans\2026-10-25-jvm-juc-ai\ai_work\sheets"
os.makedirs(OUT, exist_ok=True)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
except Exception:
    font = ImageFont.load_default()
for note in os.listdir(BASE):
    d = os.path.join(BASE, note)
    files = sorted(os.listdir(d))
    per = 24
    for si in range(0, len(files), per):
        chunk = files[si:si+per]
        cols, rows = 4, 6
        cw, ch = 400, 260
        sheet = Image.new("RGB", (cols*cw, rows*ch), "white")
        dr = ImageDraw.Draw(sheet)
        for i, fn in enumerate(chunk):
            r, c = divmod(i, cols)
            x, y = c*cw, r*ch
            try:
                im = Image.open(os.path.join(d, fn)).convert("RGB")
                im.thumbnail((cw-10, ch-30))
                sheet.paste(im, (x+5, y+25))
            except Exception as e:
                dr.text((x+5, y+5), "ERR", fill="red", font=font)
            dr.text((x+5, y+3), fn, fill="black", font=font)
        out = os.path.join(OUT, f"{note}_{si//per+1}.jpg")
        sheet.save(out, quality=88)
        print(out, len(chunk))