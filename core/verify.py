# -*- coding: utf-8 -*-
"""Строгая проверка входа: редиректу не верим, смотрим закрытую страницу."""
import re

from core import http
from modules import profiles

FORM = re.compile(r'name=["\']?(password|passwd|pwd)["\']?', re.I)
BAD = ("login_error", "неверный пароль", "incorrect password", "invalid password",
       "reauth=1")
GOOD = ("logout", "выход", "dashboard", "user_token=", "личный кабинет",
        "sign out", "log out", "профиль", "мои заказы", "панель управления")


def _paths(kind):
    prof = profiles.get(kind) or {}
    out = list(prof.get("admin") or [])[:3]
    out += ["/admin/", "/wp-admin/"]
    return out


def confirm(host, sess, kind=""):
    for p in _paths(kind):
        try:
            r = http.get(host, p, sess=sess, tries=1)
        except Exception:
            continue
        body = r.text or ""
        low = body.lower()
        url = (getattr(r, "url", "") or "").lower()
        if r.status_code != 200:
            continue
        if FORM.search(body):
            continue
        if "/wp-login.php" in url or "reauth=1" in url:
            continue
        if any(m in low for m in BAD):
            continue
        if any(g in low for g in GOOD):
            return True
    return False
