# -*- coding: utf-8 -*-
import glob
import json
import os
import re
import time
import urllib.parse

from core import config, http, ui

TPL = os.path.join(config.DATA, "templates")


def _load(only_on=True):
    out = []
    if not os.path.isdir(TPL):
        return out
    for p in sorted(glob.glob(os.path.join(TPL, "*.json"))):
        try:
            with open(p, encoding="utf-8-sig") as f:
                t = json.load(f)
            t["_file"] = os.path.basename(p)
            out.append(t)
        except Exception:
            continue
    return out


def _send(host, t, payload, timeout):
    quoted = urllib.parse.quote(payload, safe="")
    raw = t["path"]
    path = raw.replace("{{p}}", quoted) if "{{p}}" in raw else raw
    where = t.get("where") or "query"
    if where == "post-json":
        body = t["body_tpl"].replace("{{p}}", payload)
        return http.post(host, path, body, "application/json", timeout=timeout)
    if where == "post-form":
        body = (t["body_tpl"].replace("{{p}}", quoted) if t.get("body_tpl")
                else "%s=%s" % (t["param"], quoted))
        return http.post(host, path, body, referer="https://" + host + raw, timeout=timeout)
    if "{{p}}" in raw:
        return http.get(host, path, timeout=timeout)
    sep = "&" if "?" in raw else "?"
    return http.get(host, raw + sep + t["param"] + "=" + quoted, timeout=timeout)


def _ready(host, t, timeout):
    req = t.get("require")
    if not req:
        return True
    try:
        r = http.get(host, t["path"], timeout=timeout)
    except Exception:
        return False
    return req in r.text


def _verdict(t, r, elapsed, base_hash):
    body = r.text[:200000]
    for s in t.get("skip_if") or []:
        if s in body:
            return "skip"
    m = t.get("match") or {}
    kind = m.get("type")
    if kind == "time":
        return "hit" if elapsed >= float(m.get("value", 4)) else ""
    if kind == "body":
        return "hit" if m.get("value") in body else ""
    if kind == "regex":
        return "hit" if re.search(m.get("value"), body) else ""
    if kind == "status":
        return "hit" if r.status_code == int(m.get("value", 200)) else ""
    if kind == "status_diff":
        if r.status_code != int(m.get("value", 403)):
            return ""
        return "hit" if str(hash(body)) != base_hash else ""
    if kind == "diff":
        h = str(hash(body))
        return "hit" if h != base_hash else ""
    return ""


def _bool(host, t, timeout):
    """Булев матчер: сравнивает ответы на два значения между собой."""
    p1, p2 = t["payloads"][0], t["payloads"][1]
    try:
        r1 = _send(host, t, p1, timeout)
        r2 = _send(host, t, p2, timeout)
    except Exception:
        return ""
    if r1.status_code == 200 and r2.status_code != 200:
        return "hit"
    a, b = len(r1.text), len(r2.text)
    if abs(a - b) > max(200, int(a * 0.25)):
        return "hit"
    return ""


def _base_hash(host, t, timeout):
    try:
        r = http.get(host, t["path"], timeout=timeout)
        return str(hash(r.text[:200000]))
    except Exception:
        return ""


def run(host, kind="", quiet=False):
    found = []
    for t in _load():
        eng = t.get("engine") or "*"
        if eng != "*" and kind and eng != kind:
            continue
        timeout = t.get("timeout", 15)
        if not _ready(host, t, timeout):
            continue
        tid = t.get("id") or t["_file"]
        mode = (t.get("match") or {}).get("type")
        bh = _base_hash(host, t, timeout) if mode in ("diff", "status_diff") else ""
        if mode == "bool" and len(t.get("payloads") or []) >= 2:
            st = _bool(host, t, timeout)
            if st == "hit":
                found.append((tid, t["payloads"][0], t.get("score", 5)))
                if not quiet:
                    ui.ok("%s: %s" % (tid, t["payloads"][0][:50]))
            continue
        state = ""
        for payload in t.get("payloads") or []:
            t0 = time.time()
            try:
                r = _send(host, t, payload, timeout)
            except Exception:
                state = ""
                break
            state = _verdict(t, r, time.time() - t0, bh)
            if state == "skip":
                break
            if state == "hit":
                found.append((tid, payload, t.get("score", 5)))
                if not quiet:
                    ui.ok("%s: %s" % (tid, payload[:50]))
                break
        if state == "skip" and not quiet:
            ui.say("%s: не применим" % tid)
    if not found and not quiet:
        ui.say("шаблоны: пусто")
    return found
