# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\brute.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    for a in paths:
        try:
            form = _form(host, a, sess)
        except Exception:
            form = None
        if form:
            break"""
new = """    for a in paths:
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
            break"""
if s.count(old) != 1:
    print("brute: цикл не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("ок")
