# -*- coding: utf-8 -*-
"""Общий склад найденных учёток: пароль с одного хоста пробуется на других."""
import json
import os
import threading
import time

from core import config

PATH = os.path.join(config.DATA, "vault.jsonl")
_LOCK = threading.Lock()


def add(host, kind, user, pwd):
    if not user or not pwd:
        return
    row = {"host": host, "kind": kind or "", "user": user, "pass": pwd,
           "ts": int(time.time())}
    with _LOCK:
        with open(PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load():
    out = []
    if not os.path.isfile(PATH):
        return out
    with open(PATH, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def best(kind, exclude="", limit=12):
    """Сначала тот же движок и свежее, потом остальное."""
    rows = [r for r in load() if r.get("host") != exclude]
    if kind:
        rows = ([r for r in rows if r.get("kind") == kind]
                + [r for r in rows if r.get("kind") != kind])
    seen, out = [], []
    for r in sorted(rows, key=lambda x: -int(x.get("ts", 0))):
        c = "%s:%s" % (r.get("user"), r.get("pass"))
        if c not in seen:
            seen.append(c)
            out.append(c)
    return out[:limit]


def pairs(kind, exclude="", limit=12):
    out = []
    for c in best(kind, exclude, limit):
        if ":" in c:
            u, p = c.split(":", 1)
            out.append((u, p))
    return out
