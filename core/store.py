import json
import os

from core import config

CUR = os.path.join(config.PROFILES, "_current.txt")


def path(host):
    return os.path.join(config.PROFILES, host + ".json")


def get(host):
    p = path(host)
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"host": host, "url": "https://" + host + "/"}


def save(host, data):
    with open(path(host), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def current():
    if os.path.isfile(CUR):
        with open(CUR, encoding="utf-8") as f:
            v = f.read().strip()
        if v:
            return v
    return ""


def set_current(host):
    with open(CUR, "w", encoding="utf-8") as f:
        f.write(host)


def hosts():
    out = []
    for n in sorted(os.listdir(config.PROFILES)):
        if n.endswith(".json"):
            out.append(n[:-5])
    return out