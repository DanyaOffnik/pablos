# -*- coding: utf-8 -*-
import time

from core import http, ui

PRE = ("dev", "test", "old", "staging", "stage", "beta", "admin", "panel",
       "backup", "shop2", "new", "m", "portal", "crm")


def run(host):
    base = host.split(".", 1)[1] if host.count(".") >= 2 else host
    found = []
    for p in PRE:
        sub = p + "." + base
        try:
            r = http.get(sub, "/", timeout=10)
        except Exception:
            continue
        if r.status_code < 400 and len(r.content) > 800:
            ui.ok("%s  %d  %d" % (sub, r.status_code, len(r.content)))
            found.append(sub)
        time.sleep(0.3)
    if not found:
        ui.say("поддоменов не видно")
    return found