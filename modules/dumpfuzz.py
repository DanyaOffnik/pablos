# -*- coding: utf-8 -*-
"""Перебор имён резервных копий по датам. Смотрим магию файла, а не текст ошибки."""
import datetime
import time

from core import findings, http, ui

DIRS = ("/backup/", "/engine/data/", "/")
EXTS = (".sql", ".zip", ".sql.gz")
LIMIT = 90


def _names(host):
    label = host.split(".")[0]
    today = datetime.date.today()
    out = []
    for b in ("backup", "dump", "db", label):
        out.append(b)
        out.append(b + "_backup")
        for d in range(0, 10):
            day = today - datetime.timedelta(days=d)
            out.append("%s_%s" % (b, day.strftime("%Y-%m-%d")))
            out.append("%s_%s" % (b, day.strftime("%d.%m.%Y")))
            out.append("%s-%s" % (b, day.strftime("%Y%m%d")))
    seen = []
    for x in out:
        if x not in seen:
            seen.append(x)
    return seen


def _magic(r):
    head = (r.content or b"")[:600]
    low = head.lower()
    if head.startswith(b"PK"):
        return "zip"
    if head.startswith(b"\x1f\x8b"):
        return "gzip"
    if b"insert into" in low or b"create table" in low or b"-- mysql" in head.lower():
        return "sql"
    return ""


def run(host, limit=LIMIT):
    base = ""
    try:
        base = http.get(host, "/zz-%d" % int(time.time()), tries=1).text or ""
    except Exception:
        pass

    names = _names(host)
    hits = []
    tried = 0
    for d in DIRS:
        for n in names:
            for e in EXTS:
                if tried >= limit:
                    break
                tried += 1
                p = d + n + e
                try:
                    r = http.get(host, p, tries=1, timeout=12)
                except Exception:
                    continue
                if r.status_code != 200 or len(r.content) < 400:
                    continue
                kind = _magic(r)
                if not kind:
                    continue
                if base and (r.text or "")[:300] == base[:300]:
                    continue
                f = findings.make(host, "https://" + host + p, "dump:" + kind,
                                  r.status_code, len(r.content), len(base), "", "")
                hits.append(f)
                ui.ok("%s %d байт %s" % (kind, len(r.content), p))
            if tried >= limit:
                break
        if tried >= limit:
            break
    if not hits:
        ui.say("дампов не нашёл")
    return hits
