# -*- coding: utf-8 -*-
import ftplib
import re
import socket

from core import http, ui

PANELS = [("/cpanel", 2083), ("/", 2082), ("/", 8443), ("/", 2222)]


def ftp(host, user, pwd):
    for port in (21, 2121):
        try:
            c = ftplib.FTP()
            c.connect(host, port, timeout=10)
            c.login(user, pwd)
            names = c.nlst()[:6]
            c.quit()
            return True, " ".join(names)[:90]
        except Exception:
            continue
    return False, ""


def panel(host, user, pwd):
    for path, port in PANELS:
        try:
            s = socket.create_connection((host, port), timeout=5)
            s.close()
        except Exception:
            continue
        try:
            r = http.get(host + ":%d" % port, path, auth=(user, pwd), timeout=12)
        except Exception:
            continue
        if r.status_code in (200, 301, 302) and "login" not in (r.headers.get("Location") or "").lower():
            return True, "порт %d" % port
    return False, ""


def run(host, creds):
    user, _, pwd = creds.partition(":")
    out = []
    ok, extra = ftp(host, user, pwd)
    if ok:
        ui.ok("FTP ВХОД %s / %s" % (user, pwd))
        out.append("FTP:%s:%s" % (user, pwd))
    ok, extra = panel(host, user, pwd)
    if ok:
        ui.ok("ПАНЕЛЬ ВХОД %s / %s (%s)" % (user, pwd, extra))
        out.append("панель:%s:%s" % (user, pwd))
    return out