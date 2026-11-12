import json
import sys
import threading
import time
import os

from core import config, ui

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


def state_path(host):
    return os.path.join(config.SESS, host + ".json")


def load_state(host):
    p = state_path(host)
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(host, state):
    with open(state_path(host), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)
    return state_path(host)


def cookie_header(host):
    st = load_state(host)
    parts = []
    for c in st.get("cookies", []):
        parts.append("%s=%s" % (c.get("name"), c.get("value")))
    return "; ".join(parts)


LOCK = threading.Lock()

import queue

_Q = queue.Queue()
_W = None
_WL = threading.Lock()


def _loop():
    while True:
        fn, args, box, done = _Q.get()
        if fn is None:
            return
        try:
            box["r"] = fn(*args)
        except Exception as e:
            box["e"] = e
        done.set()


def _in_thread(fn, *a):
    global _W
    with _WL:
        if _W is None or not _W.is_alive():
            _W = threading.Thread(target=_loop, daemon=True)
            _W.start()
    box = {}
    done = threading.Event()
    _Q.put((fn, a, box, done))
    if not done.wait(200):
        raise RuntimeError("браузер не ответил")
    if "e" in box:
        raise box["e"]
    return box["r"]


CF = ("just a moment", "one moment, please", "checking your browser",
      "cf-browser-verification")


def _auto_body(host, url="", wait=25):
    if sync_playwright is None:
        return {}
    url = url or "https://" + host + "/"
    prof = os.path.join(config.BROWSER, host)
    os.makedirs(prof, exist_ok=True)
    st = {}
    if True:
        try:
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=prof,
                    channel="msedge",
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled", "--mute-audio"],
                )
                try:
                    page = ctx.pages[0] if ctx.pages else ctx.new_page()
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        pass
                    end = time.time() + wait
                    while time.time() < end:
                        try:
                            t = (page.title() or "").lower()
                            head = page.content()[:20000].lower()
                        except Exception:
                            break
                        if t and not any(c in t for c in CF) and "one moment" not in head:
                            break
                        time.sleep(1.5)
                    try:
                        st = ctx.storage_state()
                        st["ua"] = page.evaluate("navigator.userAgent")
                    except Exception:
                        pass
                finally:
                    try:
                        ctx.close()
                    except Exception:
                        pass
        except Exception:
            st = {}
    return st


def auto(host, url="", wait=25):
    try:
        return _in_thread(_auto_body, host, url, wait)
    except Exception:
        return {}


def auto_proc(host, url="", timeout=100):
    import subprocess
    path = os.path.join(config.SESS, host + ".auto.json")
    if os.path.isfile(path):
        os.remove(path)
    script = os.path.join(config.BASE, "core", "brfetch.py")
    try:
        subprocess.run([sys.executable, script, host, url or ""],
                       cwd=config.BASE, timeout=timeout,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return {}
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def grab(host, url=""):
    if sync_playwright is None:
        raise RuntimeError("нет playwright: pip install playwright")
    url = url or "https://" + host + "/"
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=config.BROWSER,
            channel="msedge",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        ok = False
        for i in range(4):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                ok = True
                break
            except Exception as e:
                first = str(e).splitlines()[0]
                ui.say("переход не удался, попытка %d: %s" % (i + 1, first))
                time.sleep(3)
        if not ok:
            ui.say("открой адрес руками в этом окне: " + url)
        ui.say("окно открыто: " + url)
        ui.say("пройди проверку, если она есть")
        input("  Enter когда сайт открылся: ")
        try:
            state = ctx.storage_state()
            state["ua"] = page.evaluate("navigator.userAgent")
        except Exception:
            state = ctx.storage_state()
        ctx.close()
    return state