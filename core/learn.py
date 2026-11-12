# -*- coding: utf-8 -*-
import json
import os
import threading

from core import config

PATH = os.path.join(config.DATA, "learn.json")
LOCK = threading.Lock()


def _blank():
    return {"passwords": {}, "stages": {}, "errors": {}}


def load():
    if not os.path.isfile(PATH):
        return _blank()
    try:
        with open(PATH, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return _blank()
    base = _blank()
    for k in base:
        if isinstance(d.get(k), dict):
            base[k] = d[k]
    return base


def _save(d):
    with LOCK:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)


def _bump(group, key, sub):
    d = load()
    g = d.setdefault(group, {}).setdefault(key, {})
    g[sub] = g.get(sub, 0) + 1
    _save(d)


def password_ok(kind, pwd):
    if pwd:
        _bump("passwords", kind or "?", pwd)


def stage(kind, name, hit=True):
    if name and hit:
        _bump("stages", kind or "?", name)


def error(where, msg):
    if msg:
        _bump("errors", where or "?", str(msg)[:120])


def bonus(kind, words, cap=30):
    d = load().get("passwords", {}).get(kind or "?", {})
    if not d:
        return words
    top = [p for p, _ in sorted(d.items(), key=lambda x: -x[1])][:cap]
    out = [p for p in top if p not in words] + list(words)
    return out


def top_stages(kind, cap=8):
    d = load().get("stages", {}).get(kind or "?", {})
    return [s for s, _ in sorted(d.items(), key=lambda x: -x[1])][:cap]


def top_errors(cap=10):
    d = load().get("errors", {})
    flat = []
    for where, items in d.items():
        for msg, n in items.items():
            flat.append((n, where, msg))
    flat.sort(reverse=True)
    return flat[:cap]


def show():
    d = load()
    out = []
    for kind, items in d.get("passwords", {}).items():
        top = sorted(items.items(), key=lambda x: -x[1])[:8]
        out.append("%s: %s" % (kind, ", ".join("%s(%d)" % (p, n) for p, n in top) or "-"))
    if not out:
        out.append("паролей пока нет")
    for kind, items in d.get("stages", {}).items():
        top = sorted(items.items(), key=lambda x: -x[1])[:5]
        out.append("этапы %s: %s" % (kind, ", ".join("%s(%d)" % (p, n) for p, n in top) or "-"))
    return out
