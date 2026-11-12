# -*- coding: utf-8 -*-
import hashlib
import os
import string
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import config, http, state, ui

DICT = os.path.join(config.DICT, "dirs.txt")
if not os.path.isfile(DICT):
    DICT = r"C:\work\dict\dirs.txt"
TMO = 8
DEADLINE = 600

_TL = threading.local()
_BASE = [""]


def _fp(body):
    return hashlib.sha1(body[:100000].encode("utf-8", "ignore")).hexdigest()


def _sess(host):
    s = getattr(_TL, "s", None)
    if s is None:
        s = http.session(host)
        _TL.s = s
    return s


def _base(host):
    if host.startswith("www."):
        return host
    alt = "www." + host
    try:
        r = _sess(alt).get("https://" + alt + "/", timeout=TMO, allow_redirects=True)
        if r.status_code < 500:
            return alt
    except Exception:
        pass
    return host


def _extra(kind):
    out = []
    if kind == "prestashop":
        low = string.ascii_lowercase
        out += ["admin" + a for a in low]
        out += ["admin" + a + b for a in low for b in low]
        out += ["admin%d" % i for i in range(0, 1000)]
        out += ["admin-%d" % i for i in range(0, 200)]
        out += ["admin%s" % x for x in ("dev", "shop", "panel", "site", "store", "bo", "back")]
        out += ["backoffice", "admin-dev"]
    elif kind == "opencart":
        out += ["admin", "adm", "adminpanel", "admin1", "admin2", "administrator"]
        out += ["admin%d" % i for i in range(0, 200)]
        out += ["adm%d" % i for i in range(0, 100)]
    elif kind == "bitrix":
        out += ["bitrix", "bitrix/admin"]
    elif kind == "wordpress":
        out += ["wp-admin", "wp-login.php"]
    return out


def _probe(base, name, kind=""):
    if kind in ("", "opencart"):
        try:
            r = _sess(base).get("https://" + base + "/%s/controller/common/login.php" % name,
                                timeout=TMO, allow_redirects=False)
        except Exception:
            return None
        if "Class 'Controller'" in r.text or "Class &apos;Controller" in r.text:
            return name, "oc", r.status_code
        if r.status_code != 404:
            return None
    try:
        r = _sess(base).get("https://" + base + "/%s/" % name,
                            timeout=TMO, allow_redirects=True)
    except Exception:
        return None
    if r.status_code in (401, 403):
        return name, "закрыт", r.status_code
    if r.status_code != 200:
        return None
    body = r.text
    if _fp(body) == _BASE[0]:
        return None
    low = body.lower()
    if kind == "prestashop":
        if 'name="submitlogin"' in low or 'id="login_form"' in low or "prestashop" in low:
            return name, "бэкофис", r.status_code
        return None
    if 'type="password"' in low or "user_token" in low:
        return name, "форма", r.status_code
    return None


def run(host, workers=16, dict_path=None, kind=""):
    dict_path = dict_path or DICT
    names = list(_extra(kind))
    if os.path.isfile(dict_path):
        with open(dict_path, encoding="utf-8", errors="ignore") as f:
            names += [l.strip().strip("/") for l in f if l.strip() and "/" not in l.strip()]
    names = list(dict.fromkeys(names))

    base = _base(host)
    if base != host:
        ui.say("работаю по " + base)
    try:
        r0 = _sess(base).get("https://" + base + "/zz_none_%d/" % int(time.time()),
                             timeout=TMO, allow_redirects=True)
        _BASE[0] = _fp(r0.text)
    except Exception:
        _BASE[0] = ""
    if kind:
        ui.say("движок: " + kind)
    ui.say("путей: %d" % len(names))

    found = []
    done = 0
    t0 = time.time()
    window = max(4, workers * 2)
    pending = set()
    it = iter(names)
    pool = ThreadPoolExecutor(max_workers=workers)

    def fill():
        while len(pending) < window:
            try:
                n = next(it)
            except StopIteration:
                return
            pending.add(pool.submit(_probe, base, n, kind))

    try:
        fill()
        while pending:
            fin, pending = wait(pending, return_when=FIRST_COMPLETED)
            for fut in fin:
                done += 1
                try:
                    r = fut.result()
                except Exception:
                    r = None
                if r:
                    found.append(r)
                    ui.ok("%s [%s]" % (r[0], r[1]))
            if done % 100 < len(fin):
                ui.say("%d / %d, %.0f c" % (done, len(names), time.time() - t0))
            if time.time() - t0 > DEADLINE:
                ui.warn("предел времени, встаю")
                break
            fill()
    finally:
        pool.shutdown(wait=False)

    ui.say("проверено %d за %.0f c, найдено %d" % (done, time.time() - t0, len(found)))
    if found:
        try:
            state.put(host, note="админка: " + ", ".join(f[0] for f in found[:5]))
        except Exception:
            pass
    return found


if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else ""
    if not h:
        print("укажи домен")
        sys.exit(1)
    for item in run(h, 16, sys.argv[2] if len(sys.argv) > 2 else None,
                   sys.argv[3] if len(sys.argv) > 3 else ""):
        print(*item)
