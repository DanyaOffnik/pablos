# -*- coding: utf-8 -*-
import glob
import os
import time

from PIL import Image, ImageDraw, ImageFont

from core import config

CARD = os.path.join(config.DATA, "card.png")
OUT = os.path.join(config.DATA, "cards")
FONT = r"C:\Windows\Fonts\arialbd.ttf"
POS = {"start_label": (60, 900), "start_time": (60, 980),
       "end_label": (60, 900), "end_time": (60, 980), "end_stat": (60, 1070)}
SIZES = {"label": 64, "time": 96, "stat": 44}


def _font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except Exception:
        return ImageFont.load_default()


def _put(d, xy, text, size):
    f = _font(size)
    for dx in (-3, 3):
        for dy in (-3, 3):
            d.text(xy, text, font=f, fill=(0, 0, 0))
    d.text(xy, text, font=f, fill=(255, 255, 255))


def start(name, at):
    return _draw("start", name, [("start_label", "НАЧАЛО", "label"),
                                 ("start_time", at, "time")])


def end(name, at, stat=""):
    return _draw("end", name, [("end_label", "КОНЕЦ", "label"),
                               ("end_time", at, "time"), ("end_stat", stat, "stat")])


def _draw(kind, name, items):
    if not os.path.isfile(CARD):
        return ""
    os.makedirs(OUT, exist_ok=True)
    img = Image.open(CARD).convert("RGB")
    d = ImageDraw.Draw(img)
    for key, text, sz in items:
        if text:
            _put(d, POS[key], text, SIZES[sz])
    path = os.path.join(OUT, "%s_%s_%d.png" % (kind, name, int(time.time())))
    img.save(path, "PNG")
    files = sorted(glob.glob(os.path.join(OUT, "*.png")))
    for old in files[:-20]:
        try:
            os.remove(old)
        except Exception:
            pass
    return path
