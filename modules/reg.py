# -*- coding: utf-8 -*-
"""Открытая регистрация. Заведённая учётка даёт больше, чем гость."""
import random
import re
import string

from core import findings, http, ui

PATHS = {
    "wordpress": ["/wp-login.php?action=register"],
    "joomla": ["/index.php?option=com_users&view=registration",
               "/component/users/?view=registration"],
    "dle": ["/index.php?do=register", "/index.php?do=lostpassword"],
    "bitrix": ["/?register=yes", "/auth/?register=yes"],
    "opencart": ["/index.php?route=account/register"],
    "prestashop": ["/index.php?controller=authentication&create_account=1"],
    "laravel": ["/register"],
    "django": ["/accounts/signup/", "/register/"],
}

PASS = re.compile(r'<input[^>]*type="?password', re.I)
MAIL = re.compile(r'<input[^>]*type="?email', re.I)
LOGIN = re.compile(r'<input[^>]*name="?([a-z_]*(?:login|user|name|nick)[a-z_]*)"?', re.I)


def _creds(host):
    tag = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
    return "%s_%s" % (host.split(".")[0][:8], tag), "%s@%s" % (tag, host), "Aa9!" + tag


def _fields(html):
    out = {}
    for m in re.finditer(r"<input[^>]*>", html, re.I):
        tag = m.group(0)
        nm = re.search(r'name="([^"]+)"', tag)
        if not nm:
            continue
        out[nm.group(1)] = re.search(r'value="([^"]*)"', tag)
    return out


def run(host, kind=""):
    got = []
    for p in PATHS.get(kind or "", []) or []:
        try:
            r = http.get(host, p, tries=1, timeout=12)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        body = r.text or ""
        if not (PASS.search(body) and MAIL.search(body)):
            continue
        ui.ok("форма регистрации: " + p)
        got.append(findings.make(host, "https://" + host + p, "register", r.status_code,
                                 len(body), 0, body, "", kind))
        if kind == "wordpress":
            user, mail, pwd = _creds(host)
            body_post = ("user_login=%s&user_email=%s&wp-submit=Register"
                         "&redirect_to=%%2Fwp-login.php%%3Fcheckemail%%3Dconfirm" % (user, mail))
            try:
                w = http.post(host, p, body_post, referer="https://" + host + p, tries=1)
            except Exception as e:
                ui.say("сбой: %s" % e)
                continue
            low = (w.text or "").lower()
            if "checkemail" in w.url or "регистрац" in low or "registered" in low:
                ui.ok("ЗАВЁЛ: %s / %s" % (user, pwd))
                got.append(findings.make(host, "https://" + host + p, "register-ok",
                                         w.status_code, len(w.content or b""), 0, w.text,
                                         "%s:%s" % (user, pwd), kind))
    if not got:
        ui.say("регистрация закрыта")
    return got
