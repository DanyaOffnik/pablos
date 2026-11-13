# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\core\http.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT, verify=False,
                     http2=False)"""
new = """    try:
        s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT,
                         verify=False, http2=False)
    except TypeError:
        s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT, verify=False)"""
if s.count(old) != 1:
    print("http: не найдено"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("ок")
