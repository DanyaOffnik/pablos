# -*- coding: utf-8 -*-
import time

from core import http, ui

MARKS = [
    ("opencart", ("route=product", "catalog/view", "index.php?route=", "oc_", "ocstore")),
    ("wordpress", ("wp-content", "wp-includes", "wp-json")),
    ("bitrix", ("/bitrix/", "bitrix24")),
    ("shopify", ("cdn.shopify", "shopify")),
    ("horoshop", ("horoshop",)),
    ("promua", ("prom.ua", "promgroup")),
    ("laravel", ("laravel", "csrf-token")),
    ("prestashop", ("prestashop", "modules/ps_")),
    ("django", ("csrfmiddlewaretoken", "django")),
    ("frappe", ("frappe", "desk#", "/assets/frappe/")),
]


def detect(host):
    r = None
    for _ in range(2):
        try:
            r = http.get(host, "/", timeout=20)
            break
        except Exception:
            time.sleep(1.5)
    if r is None:
        return "нет связи", ""
    if r.status_code == 200:
        try:
            p = http.get(host, "/api/method/ping", timeout=10)
            if "pong" in p.text.lower():
                return "frappe", r.text[:120000].lower()
        except Exception:
            pass
    if r.status_code != 200:
        return "код %d" % r.status_code, ""
    body = r.text[:120000].lower()
    for name, keys in MARKS:
        for k in keys:
            if k in body:
                return name, body
    return "неизвестно", body


import re

VER = {
    "opencart": [re.compile(r"(?:OpenCart|ocStore)\s*([0-9][0-9.]{1,10})", re.I)],
    "wordpress": [re.compile(r'content="WordPress\s*([0-9.]+)', re.I),
                  re.compile(r"wp-includes/css/[^\"']*?ver=([0-9.]+)")],
    "bitrix": [re.compile(r"bitrix[^0-9]{0,20}([0-9]{2}\.[0-9.]+)", re.I)],
    "prestashop": [re.compile(r"PrestaShop\s*([0-9.]+)", re.I)],
}


def version(host, kind):
    paths = ["/"] + (["/admin/"] if kind == "opencart" else [])
    for p in paths:
        try:
            r = http.get(host, p, timeout=15)
        except Exception:
            continue
        body = r.text[:200000]
        for rx in VER.get(kind, []):
            m = rx.search(body)
            if m:
                return m.group(1)
    return ""


def run(host):
    kind, _ = detect(host)
    if kind == "нет связи":
        ui.err("сайт не открылся")
    elif kind == "opencart":
        ui.ok("движок: opencart — работаем")
    else:
        ui.warn("движок: %s — наборы путей заточены под opencart" % kind)
