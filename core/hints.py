# -*- coding: utf-8 -*-
"""Подсказки по версии: что применимо."""

MAP = [
    ("3.0.3", "Divido SQLi (CVE-2024-21514), проверь /index.php?route=extension/payment/divido/callback/confirm"),
    ("3.0.2", "старая ветка, много модулей с инъекциями, пробуй параметры filter_*"),
    ("3.0.1", "старая ветка, пробуй install/ и старые модули"),
    ("3.0.0", "старая ветка, пробуй install/ и старые модули"),
    ("2.3", "старый OpenCart: инъекции в filter_*, upload через модули"),
    ("2.1", "очень старый: известные RCE в модулях, пробуй /install/"),
    ("1.5", "древний: SQLi в search и product, обычно без защиты"),
]

WP = [
    ("6.4", "WordPress 6.4: смотри плагины, обновляй список путей"),
    ("6.3", "WordPress 6.3: перебор плагинов и xmlrpc"),
    ("5.", "старый WordPress: xmlrpc.php, перебор пользователей через ?author="),
]


def get(kind, ver):
    if not ver:
        return ""
    table = WP if kind == "wordpress" else MAP
    for pre, text in table:
        if str(ver).startswith(pre):
            return text
    return ""
