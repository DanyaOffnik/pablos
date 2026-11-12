# -*- coding: utf-8 -*-
"""Пул прокси: импорт, проверка, чистка."""
import concurrent.futures as cf
import os

from curl_cffi import requests as creq

from core import config, ui

CHECK = "http://api.ipify.org"


def load():
    if not os.path.isfile(config.PROXIES):
        return []
    out = []
    with open(config.PROXIES, encoding="utf-8") as f:
        for line in f:
            p = line.strip()
            if p and not p.startswith("#"):
                out.append(p if "://" in p else "http://" + p)
    return out


def save(items):
    with open(config.PROXIES, "w", encoding="utf-8") as f:
        for p in items:
            f.write(p + "\n")


def _one(p, timeout=9):
    try:
        r = creq.get(CHECK, proxies={"http": p, "https": p},
                     impersonate="chrome", timeout=timeout)
        ip = (r.text or "").strip()
        if r.status_code == 200 and 7 <= len(ip) <= 45 and " " not in ip:
            return p
    except Exception:
        pass
    return ""


def import_file(path):
    if not os.path.isfile(path):
        ui.err("файла нет")
        return 0
    got = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            p = line.strip().split()[0] if line.strip() else ""
            if not p or p.startswith("#"):
                continue
            p = p if "://" in p else "http://" + p
            if p.count(":") >= 2:
                got.append(p)
    cur = load()
    add = [p for p in dict.fromkeys(got) if p not in cur]
    save(cur + add)
    ui.ok("добавлено: %d, всего: %d" % (len(add), len(cur) + len(add)))
    return len(add)


def check_all(workers=20):
    items = load()
    if not items:
        ui.say("файл пуст")
        return 0, 0
    ui.say("проверяю: %d" % len(items))
    good = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, res in enumerate(ex.map(_one, items), 1):
            if res:
                good.append(res)
            if i % 25 == 0:
                ui.say("  %d / %d, живых %d" % (i, len(items), len(good)))
    save(good)
    return len(good), len(items)
