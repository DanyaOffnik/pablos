# -*- coding: utf-8 -*-
from core import http, ui

PATHS = [
    ("/", "главная"),
    ("/admin/", "админка"),
    ("/admin/index.php?route=common/login", "вход в админку"),
    ("/adminer.php", "adminer"),
    ("/phpinfo.php", "phpinfo"),
    ("/info.php", "info"),
    ("/.env", "env"),
    ("/.env.bak", "env bak"),
    ("/error_log", "error_log"),
    ("/debug.log", "debug.log"),
    ("/robots.txt", "robots"),
    ("/sitemap.xml", "sitemap"),
    ("/composer.json", "composer"),
    ("/README.md", "readme"),
]


def _title(body):
    low = body.lower()
    if "<title>" not in low:
        return ""
    a = low.index("<title>") + 7
    b = low.find("</title>", a)
    if b < 0:
        return ""
    return body[a:b].strip()[:70]


def run(host):
    home = None
    hits = []
    for path, name in PATHS:
        try:
            r = http.get(host, path, referer="https://" + host + "/")
        except Exception as e:
            ui.say("%-30s сбой: %s" % (name, str(e).splitlines()[0]))
            continue
        size = len(r.content)
        title = _title(r.text)
        if path == "/":
            home = (r.status_code, size, title)
        mark = ""
        if r.status_code == 200:
            if path == "/":
                mark = "база"
            elif home and size == home[1] and title == home[2]:
                mark = "как главная"
            elif size < 1200:
                mark = "мало"
            else:
                mark = "ОТЛИЧАЕТСЯ"
                hits.append((path, name, size))
        ui.say("%-30s %d %6d %s %s" % (path, r.status_code, size, title, mark))
    print()
    if hits:
        ui.say("интересное:")
        for path, name, size in hits:
            ui.say("  %s (%s) - %d байт" % (path, name, size))
    else:
        ui.say("ничего не выделилось")
