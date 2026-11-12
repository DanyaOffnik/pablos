# -*- coding: utf-8 -*-
"""Определение логинов до перебора. Кэш в data/users.json."""
import json
import os
import re

from core import config, http

DB = os.path.join(config.DATA, "users.json")


def _load():
    try:
        with open(DB, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(host, names):
    db = _load()
    db[host] = names
    try:
        os.makedirs(os.path.dirname(DB), exist_ok=True)
        with open(DB, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def _wordpress(host, sess):
    out = []
    try:
        r = http.get(host, "/wp-json/wp/v2/users?per_page=100", sess=sess, tries=0)
        if r.status_code == 200:
            out += re.findall(r'"slug"\s*:\s*"([^"]+)"', r.text)
    except Exception:
        pass
    if not out:
        for i in range(1, 6):
            try:
                r = http.get(host, "/?author=%d" % i, sess=sess, tries=0)
                u = getattr(r, "url", "") or ""
                m = re.search(r"/author/([^/?#]+)", u)
                if m and m.group(1) not in out:
                    out.append(m.group(1))
            except Exception:
                pass
    return out


def _from_login_page(host, path, sess):
    """Иногда форма сама подсказывает логин в value или placeholder."""
    out = []
    try:
        r = http.get(host, path, sess=sess, tries=0)
        for m in re.finditer(r'name=["\'](?:log|login|username|user|email)["\'][^>]*'
                             r'(?:value|placeholder)=["\']([^"\']{2,40})["\']', r.text, re.I):
            v = m.group(1).strip()
            if v and "@" not in v and v.lower() not in ("login", "user", "email"):
                out.append(v)
    except Exception:
        pass
    return out


def get(host, kind="", sess=None):
    db = _load()
    if host in db:
        return db[host]
    out = []
    if kind == "wordpress":
        out += _wordpress(host, sess)
    if not out:
        out += _from_login_page(host, "/wp-login.php", sess)
        out += _from_login_page(host, "/admin/", sess)
    seen = []
    for x in out:
        x = x.strip()
        if x and x not in seen:
            seen.append(x)
    if seen:
        _save(host, seen)
    return seen
