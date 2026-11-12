# -*- coding: utf-8 -*-
import json
import os
import socket
import time

from core import config

ORDER = ("new", "scanned", "hot", "dossier", "manual", "cracked", "trash")
ACTIVE = ("new", "scanned", "hot", "dossier", "manual")


def machine():
    p = os.path.join(config.DATA, "settings.json")
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                v = json.load(f).get("machine")
            if v:
                return str(v)
        except Exception:
            pass
    return socket.gethostname().lower()[:20]


def _name(host):
    return host.replace("/", "_").replace(":", "_").lower() + ".json"


def _path(host):
    return os.path.join(config.STATE, _name(host))


def _lock(host):
    return os.path.join(config.LEASE, _name(host) + ".lock")


def get(host):
    p = _path(host)
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"host": host, "status": "new", "score": 0, "note": ""}


def put(host, **kw):
    d = get(host)
    d.update(kw)
    d["host"] = host
    d["at"] = time.strftime("%Y-%m-%d %H:%M")
    d["machine"] = machine()
    tmp = _path(host) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _path(host))
    return d


def status(host):
    return get(host).get("status", "new")


def set_status(host, st, note=None, score=None):
    if st not in ORDER:
        raise ValueError("неизвестный статус: " + st)
    kw = {"status": st}
    if note is not None:
        kw["note"] = note
    if score is not None:
        kw["score"] = score
    return put(host, **kw)


def _read_lock(host):
    p = _lock(host)
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def is_locked(host, ttl=None):
    d = _read_lock(host)
    if not d:
        return False
    if d.get("machine") == machine():
        return False
    ttl = ttl or config.LEASE_TTL
    return time.time() - float(d.get("ts", 0)) < ttl


def acquire(host, ttl=None):
    if is_locked(host, ttl):
        return False
    with open(_lock(host), "w", encoding="utf-8") as f:
        json.dump({"machine": machine(), "ts": time.time()}, f)
    return True


def touch(host):
    if _read_lock(host):
        with open(_lock(host), "w", encoding="utf-8") as f:
            json.dump({"machine": machine(), "ts": time.time()}, f)


def release(host):
    try:
        os.remove(_lock(host))
    except Exception:
        pass


def by_status(st):
    out = []
    for n in os.listdir(config.STATE):
        if not n.endswith(".json"):
            continue
        p = os.path.join(config.STATE, n)
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        if d.get("status") == st:
            out.append(d)
    out.sort(key=lambda x: -(x.get("score") or 0))
    return out


def counts():
    res = {k: 0 for k in ORDER}
    for n in os.listdir(config.STATE):
        if not n.endswith(".json"):
            continue
        try:
            with open(os.path.join(config.STATE, n), encoding="utf-8") as f:
                s = json.load(f).get("status", "new")
        except Exception:
            continue
        if s in res:
            res[s] += 1
    return res
