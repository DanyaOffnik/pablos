# -*- coding: utf-8 -*-
import os
import time

from core import config, http, ui

NAMES = ("backup", "db", "dump", "site", "www", "<label>")
EXT = (".zip", ".sql", ".tar.gz")


def candidates(host):
    label = host.split(".")[0]
    out = []
    for name in NAMES:
        name = name.replace("<label>", label)
        out.append("/" + name + ".zip")
        out.append("/" + name + ".sql")
    out += ["/backup_2024.zip", "/backup_2025.zip", "/db_2024.sql",
            "/site_2025.zip", "/public_html.zip", "/" + label + ".tar.gz"]
    seen = []
    for x in out:
        if x not in seen:
            seen.append(x)
    return seen[:22]


def _real(r):
    if r.status_code != 200 or len(r.content) < 4000:
        return ""
    head = r.content[:400]
    if head[:2] == b"PK":
        return "ZIP"
    if head[:2] == b"\x1f\x8b":
        return "GZ"
    if b"Rar!" in head[:8]:
        return "RAR"
    if head[:6] == b"7z\xbc\xaf\x27\x1c":
        return "7Z"
    if b"CREATE TABLE" in r.content[:200000] or b"INSERT INTO" in r.content[:200000]:
        return "SQL"
    return ""


def run(host):
    hits = []
    t0 = time.time()
    for path in candidates(host):
        if time.time() - t0 > 55:
            break
        try:
            r = http.get(host, path, timeout=10)
        except Exception:
            continue
        kind = _real(r)
        if kind:
            size = len(r.content)
            ui.ok("%s  %s  %d КБ" % (path, kind, size // 1024))
            hits.append((path, kind, size))
            if size > 20000:
                d = os.path.join(config.LOGS, "arch")
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, host + path.replace("/", "_")), "wb") as f:
                    f.write(r.content)
            if len(hits) >= 4:
                break
        time.sleep(0.2)
    if not hits:
        ui.say("архивов не нашёл")
    return hits