"""Automatic target discovery from descriptor footprint.

Bing RSS (format=rss) is the working free provider: stable markup, no
captcha wall. Footprint lines use the inurl: form with slashes on both
ends, otherwise Bing returns nothing. Shodan joins in when keyed.
"""
import json
import os
import random
import re
import time
import urllib.parse

from core import http

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "vuln")
KEYS = os.path.join(DB, "_keys.json")

SKIP = {"duckduckgo.com", "bing.com", "google.com", "yandex.ru", "youtube.com",
        "wikipedia.org", "facebook.com", "twitter.com", "x.com", "wordpress.org",
        "github.com", "linkedin.com", "reddit.com", "medium.com", "microsoft.com",
        "cloudflare.com", "stackoverflow.com", "infobel.com", "lidl.ro", "lidl.dk",
        "lidl.bg", "lidl.pl", "lidl.cz", "lidl.hu", "lidl.sk"}


def _get(host, path, tries=1):
    return http.request(host, path, tries=tries)


def _clean(hosts):
    out = set()
    for h in hosts:
        h = (h or "").strip().lower().rstrip(".")
        if not h or "." not in h:
            continue
        if any(h == s or h.endswith("." + s) for s in SKIP):
            continue
        out.add(h)
    return out


def _query(v):
    for line in v.get("footprint", []):
        if "inurl:" in line:
            return line.split("inurl:", 1)[1].strip().strip('"')
    plug = v.get("plugin")
    if plug:
        return "/wp-content/plugins/%s/" % plug
    return ""


def _links(text):
    return re.findall(r"<link>(https?://[^<]+)</link>", text or "")


def _variants(q):
    q = q.strip("/")
    if not q:
        return []
    slug = q.rsplit("/", 1)[-1]
    out = ["/" + q + "/", "/" + q]
    if slug and slug not in out:
        out.append(slug)
    return out


def _page(q, page, attempts=8):
    path = ("/search?q=" + urllib.parse.quote("inurl:" + q)
            + "&format=rss&count=50&first=%d" % (page * 10 + 1))
    slug = q.strip("/").rsplit("/", 1)[-1]
    for _ in range(attempts):
        http.drop("www.bing.com")
        try:
            r = _get("www.bing.com", path)
        except Exception:
            time.sleep(2.0)
            continue
        if getattr(r, "status_code", 0) != 200:
            time.sleep(2.0)
            continue
        links = _links(getattr(r, "text", ""))
        hit = {urllib.parse.urlparse(u).hostname for u in links
               if slug and slug in u}
        hit = _clean(hit)
        if hit:
            return hit
        time.sleep(2.0)
    return set()


def _bing(q, limit):
    got = set()
    for v in _variants(q):
        for page in range(0, 6):
            part = _page(v, page)
            if not part:
                break
            before = len(got)
            got |= part
            if len(got) >= limit:
                return got
            if len(got) == before and page > 1:
                break
            time.sleep(random.uniform(1.2, 2.5))
    return got


def _ddg(q, limit):
    got = set()
    for page in range(0, max(1, limit // 20)):
        path = "/lite/?q=" + urllib.parse.quote("inurl:" + q) + "&s=%d" % (page * 20)
        try:
            r = _get("lite.duckduckgo.com", path)
        except Exception:
            break
        text = getattr(r, "text", "") or ""
        if getattr(r, "status_code", 0) != 200 or "anomaly" in text:
            break
        for m in re.finditer(r"uddg=([^&\"]+)", text):
            h = urllib.parse.urlparse(urllib.parse.unquote(m.group(1))).hostname
            if h:
                got.add(h)
        if not got:
            break
        time.sleep(random.uniform(2.5, 5.0))
    return _clean(got)


def _shodan(q, limit):
    if not os.path.isfile(KEYS):
        return set()
    try:
        key = json.load(open(KEYS, encoding="utf-8")).get("shodan")
    except Exception:
        return set()
    if not key:
        return set()
    got = set()
    for page in range(1, 6):
        path = ("/shodan/host/search?key=%s&query=%s&page=%d"
                % (key, urllib.parse.quote('http.html:"%s"' % q), page))
        try:
            r = _get("api.shodan.io", path)
            data = json.loads(getattr(r, "text", "{}"))
        except Exception:
            break
        if "matches" not in data:
            break
        for m in data["matches"]:
            hn = m.get("hostnames") or []
            if hn:
                got.add(hn[0])
        if len(got) >= limit:
            break
        time.sleep(1.2)
    return _clean(got)


def collect(cve_id, limit=100, providers=None):
    v = json.load(open(os.path.join(DB, cve_id, "vuln.json"), encoding="utf-8"))
    q = _query(v)
    if not q:
        return []
    providers = providers or ["bing", "shodan", "ddg"]
    got = set()
    for p in providers:
        if len(got) >= limit:
            break
        fn = {"bing": _bing, "ddg": _ddg, "shodan": _shodan}.get(p)
        if not fn:
            continue
        try:
            got |= fn(q, limit - len(got))
        except Exception:
            continue
    return sorted(got)[:limit]