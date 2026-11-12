# -*- coding: utf-8 -*-
import re

from core import http, ui

VULN = {
    "wp-file-manager": ("6.5", "ниже 6.5 — загрузка и запуск PHP без входа"),
    "duplicator": ("1.3.26", "ниже 1.3.26 — чтение произвольных файлов"),
    "all-in-one-wp-migration": ("7.60", "ниже 7.60 — выгрузка базы без входа"),
    "elementor": ("3.6", "ниже 3.6 — загрузка файлов"),
    "backup-backup": ("1.1.6", "ниже 1.1.6 — чтение файлов"),
    "wp-optimize": ("3.1.3", "ниже 3.1.3 — SQL-инъекция"),
    "instagram-feed": ("2.9", "ниже 2.9 — инъекция"),
    "litespeed-cache": ("4.6", "ниже 4.6 — обход авторизации"),
    "really-simple-ssl": ("4.0", "ниже 4.0 — обход авторизации"),
    "woocommerce": ("7.0", "ниже 7.0 — инъекции в параметрах"),
    "contact-form-7": ("5.8", "ниже 5.8 — обход и инъекции"),
    "js_composer": ("6.9", "ниже 6.9 — загрузка файлов"),
}


def _older(cur, limit):
    def parts(v):
        out = []
        for x in v.split("."):
            d = "".join(c for c in x if c.isdigit())
            out.append(int(d) if d else 0)
        return out
    a, b = parts(cur), parts(limit)
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return a < b


TAG = re.compile(r"stable tag:\s*([0-9a-z.\-]+)", re.I)


def _ver(text):
    m = TAG.search(text)
    return m.group(1) if m else ""


def run(host, plugins):
    hits = []
    for p in plugins:
        try:
            r = http.get(host, "/wp-content/plugins/%s/readme.txt" % p, timeout=12)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        v = _ver(r.text)
        if not v:
            continue
        info = VULN.get(p)
        if info and _older(v, info[0]):
            ui.warn("%s %s — %s" % (p, v, info[1]))
            hits.append("%s %s" % (p, v))
        else:
            ui.say("%s %s" % (p, v))
    return hits