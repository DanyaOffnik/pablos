# -*- coding: utf-8 -*-
import re

from core import http, ui

RX = [
    re.compile(r"oct_[a-z0-9_]{2,30}", re.I),
    re.compile(r"extension/module/([a-z0-9_]{2,30})", re.I),
    re.compile(r"journal|revolution|hypermark|sstore|kuler|avocado", re.I),
    re.compile(r"module/([a-z0-9_]{3,30})", re.I),
]
SKIP = {"index", "common", "product", "module", "catalog", "image", "catalog/view"}


def list_mods(host):
    body = ""
    for p in ("/", "/index.php?route=common/home"):
        try:
            r = http.get(host, p)
        except Exception:
            continue
        body += r.text[:200000]
        if len(body) > 200000:
            break
    found = []
    low = body.lower()
    for rx in RX:
        for m in rx.findall(body):
            name = (m if isinstance(m, str) else m[0]).lower()
            if name in SKIP or len(name) < 3:
                continue
            if name not in found:
                found.append(name)
    if "oct_" in low or "journal" in low:
        for key in ("oct_quick_order", "oct_feedback", "oct_blogarticle", "oct_popup_call"):
            if key in low and key not in found:
                found.append(key)
    return found[:25]


def routes(mods_list):
    out = []
    for m in mods_list:
        if m.startswith("oct_"):
            out.append(("/index.php?route=extension/module/" + m, "product_id", "1"))
        elif m in ("journal", "revolution"):
            out.append(("/index.php?route=extension/module/" + m, "id", "1"))
    return out[:6]


def run(host):
    got = list_mods(host)
    if not got:
        ui.say("сторонних модулей не видно")
        return []
    ui.say("модули: " + ", ".join(got))
    return got
