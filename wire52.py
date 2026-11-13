# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """        _, score, notes_s, title = data"""
new = """        _, score, notes_s, title, _finds = data"""
if s.count(old) != 1:
    print("night: распаковка не найдена"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("ок")
