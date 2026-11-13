# -*- coding: utf-8 -*-
import io
import os
import threading
import time
import zlib
from collections import OrderedDict

from curl_cffi import requests as creq

from core import browser, config

SESS_MAX = 32
PROX_MAX = 512
BAD_LIMIT = 3
RETRIES = 2

_LOCK = threading.Lock()
_PROX = OrderedDict()
_BAD = {}
_SEQ = {}
_SESS = OrderedDict()


def _pool():
    if not os.path.isfile(config.PROXIES):
        return []
    out = []
    with open(config.PROXIES, encoding="utf-8") as f:
        for line in f:
            p = line.strip()
            if not p or p.startswith("#"):
                continue
            if "://" not in p:
                p = "http://" + p
            out.append(p)
    return out


def proxy_for(host):
    with _LOCK:
        if host in _PROX:
            _PROX.move_to_end(host)
            return _PROX[host]
    pool = [p for p in _pool() if _BAD.get(p, 0) < BAD_LIMIT]
    if not pool:
        with _LOCK:
            _BAD.clear()
        pool = _pool()
    if not pool:
        return ""
    with _LOCK:
        n = _SEQ.get(host, 0)
    p = pool[(zlib.crc32(host.encode()) + n) % len(pool)]
    with _LOCK:
        _PROX[host] = p
        _PROX.move_to_end(host)
        while len(_PROX) > PROX_MAX:
            _PROX.popitem(last=False)
    return p


def _dec(r):
    enc = (r.headers.get("content-encoding") or "").lower()
    if not enc or not r.content:
        return r
    try:
        raw = r.content
        if enc == "zstd":
            import zstandard
            with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)) as rd:
                raw = rd.read()
        elif enc == "br":
            import brotli
            raw = brotli.decompress(raw)
        elif enc == "deflate":
            raw = zlib.decompress(raw)
        else:
            return r
        r._content = raw
        r.headers["content-encoding"] = "identity"
    except Exception:
        pass
    return r


def _bad(px):
    with _LOCK:
        _BAD[px] = _BAD.get(px, 0) + 1


def session(host):
    try:
        s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT,
                         verify=False, http2=False)
    except TypeError:
        s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT, verify=False)
    s.headers["Accept-Encoding"] = "gzip, deflate, br"
    px = proxy_for(host)
    if px:
        s.proxies = {"http": px, "https": px}
    st = browser.load_state(host)
    if st.get("ua"):
        s.headers["User-Agent"] = st["ua"]
    for c in st.get("cookies", []):
        try:
            s.cookies.set(c["name"], c["value"], domain=c.get("domain") or host)
        except Exception:
            pass
    return s


def persist(host):
    with _LOCK:
        s = _SESS.get(host)
        if s is not None:
            _SESS.move_to_end(host)
            return s
    s = session(host)
    with _LOCK:
        _SESS[host] = s
        _SESS.move_to_end(host)
        while len(_SESS) > SESS_MAX:
            _SESS.popitem(last=False)
    return s


def drop(host):
    with _LOCK:
        _SESS.pop(host, None)
        _PROX.pop(host, None)
        _SEQ[host] = _SEQ.get(host, 0) + 1


release = drop


def request(host, path, method="GET", body=None, ctype="", referer="", auth=None,
            timeout=None, sess=None, tries=None):
    url = path if path.startswith("http") else "https://" + host + path
    h = {}
    if referer:
        h["Referer"] = referer
    if ctype:
        h["Content-Type"] = ctype
    kw = {"headers": h, "allow_redirects": True,
          "timeout": timeout or config.TIMEOUT}
    if auth:
        kw["auth"] = auth
    if method == "POST":
        kw["data"] = body or ""

    last = None
    last_r = None
    for attempt in range((RETRIES if tries is None else tries) + 1):
        s = sess or session(host)
        try:
            r = s.request(method, url, **kw)
        except Exception as e:
            last = e
            msg = str(e)
            if "HTTP/2" in msg or "stream" in msg or "reset by server" in msg:
                drop(host)
                time.sleep(0.4)
                continue
            if not sess:
                px = _PROX.get(host)
                if px:
                    _bad(px)
                drop(host)
            time.sleep(0.6 * (attempt + 1))
            continue
        last_r = r
        _dec(r)
        if r.status_code in (429, 503) and attempt < RETRIES:
            time.sleep(1.2 * (attempt + 1))
            continue
        return r
    if last_r is not None:
        return last_r
    if last is not None:
        raise last
    raise RuntimeError("request failed")


def get(host, path="/", referer="", auth=None, timeout=None, sess=None, tries=None):
    return request(host, path, referer=referer, auth=auth, timeout=timeout,
                   sess=sess, tries=tries)


def post(host, path, body="", ctype="application/x-www-form-urlencoded", referer="",
         timeout=None, sess=None, tries=None):
    return request(host, path, "POST", body, ctype, referer, timeout=timeout,
                   sess=sess, tries=tries)
