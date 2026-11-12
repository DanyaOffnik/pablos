# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\modules\brute.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
"""def _form(host, path, sess):""",
"""WP_PATHS = ("/wp-login.php", "/wp-admin/")
COMMON = ("/login", "/login/", "/signin", "/sign-in", "/admin/", "/administrator/",
          "/manager/", "/panel/", "/cabinet/", "/lk/", "/account/", "/my-account/",
          "/bitrix/admin/", "/user/login", "/admin/login", "/auth/login",
          "/administrator/index.php", "/index.php?route=common/login")


def _has_pass(html):
    return bool(re.search(r'<input[^>]*type=[\\"\\']?password', html, re.I))


def _final(r):
    try:
        u = r.url or ""
        return "/" + (u.split("/", 3)[-1] or "")
    except Exception:
        return ""


def _discover(host, sess, prof):
    \"\"\"Настоящая форма входа: редиректы с wp-login, robots, типовые пути.\"\"\"
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


def _form(host, path, sess):"""))

PAIRS.append((
"""    html = r.text
    if not _loginish(html):
        return None""",
"""    html = r.text
    if not _loginish(html) and not _has_pass(html):
        return None"""))

PAIRS.append((
"""    paths = [login] if login else list(prof.get("admin") or [])[:4] + _links(host, sess)""",
"""    paths = [login] if login else _discover(host, sess, prof)"""))

for i, (old, new) in enumerate(PAIRS, 1):
    n = s.count(old)
    if n != 1:
        print("ЗАМЕНА %d: найдено %d, стоп" % (i, n))
        sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("discover: ок")
