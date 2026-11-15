"""Multi-oracle version resolution.

One oracle is a guess. Several independent ones with weights are a
measurement. Behaviour probes yield no version but prove the endpoint
is live and unpatched.
"""
import hashlib
import json
import os
import re

WEIGHTS = {"readme": 2, "asset_ver": 2, "hash": 4, "behavior": 5}


def _w(o):
    return int(o.get("w", WEIGHTS.get(o.get("kind"), 1)))


def _sha1(data):
    return hashlib.sha1(data).hexdigest()


def _load_map(o, base_dir):
    if "map" in o:
        return o["map"]
    p = o.get("map_file")
    if not p:
        return {}
    if not os.path.isabs(p):
        p = os.path.join(base_dir, p)
    if not os.path.isfile(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _body(r):
    c = getattr(r, "content", None)
    if isinstance(c, (bytes, bytearray)):
        return bytes(c)
    return (getattr(r, "text", "") or "").encode("utf-8", "ignore")


def evaluate(base, oracles, fetch, base_dir="."):
    votes = {}
    evidence = []
    alive = False

    for o in oracles:
        kind = o.get("kind")
        path = o.get("path", "")
        if not path:
            continue
        try:
            r = fetch("GET", base + path)
        except Exception as e:
            evidence.append("%s:%s" % (kind, type(e).__name__))
            continue

        code = getattr(r, "status_code", 0) or 0
        text = getattr(r, "text", "") or ""
        if code != 200:
            evidence.append("%s:%s" % (kind, code))
            continue

        if kind == "behavior":
            exp = o.get("expect", "")
            if exp and exp in text:
                alive = True
                evidence.append("behavior:alive")
            else:
                evidence.append("behavior:miss")
            continue

        ver = None
        if kind == "hash":
            ver = _load_map(o, base_dir).get(_sha1(_body(r)))
        elif o.get("regex"):
            m = re.search(o["regex"], text)
            ver = m.group(1) if m else None

        if not ver:
            evidence.append("%s:no-version" % kind)
            continue

        votes[ver] = votes.get(ver, 0) + _w(o)
        evidence.append("%s:%s" % (kind, ver))

    if not votes:
        return {"version": None, "alive": alive, "evidence": evidence,
                "conflict": False, "votes": {}}

    ranked = sorted(votes.items(), key=lambda kv: -kv[1])
    conflict = len(ranked) > 1 and (ranked[0][1] - ranked[1][1]) <= 1
    return {"version": ranked[0][0], "alive": alive, "evidence": evidence,
            "conflict": conflict, "votes": votes}