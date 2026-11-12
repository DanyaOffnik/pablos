# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\mass.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """FAST = 6
SLOW = 10"""
new = """FAST = 6
SLOW = 10
MIN = 3"""
if s.count(old) != 1:
    print("mass: константы не найдены"); sys.exit(1)
s = s.replace(old, new)

old2 = """    good = [r[0] for r in rows if r[1] > 0]
    junk = [r[0] for r in rows if r[1] <= 0 and r[0] != "?"]"""
new2 = """    good = [r[0] for r in rows if r[1] >= MIN and r[4]]
    junk = [r[0] for r in rows if (r[1] < MIN or not r[4]) and r[0] != "?"]"""
if s.count(old2) != 1:
    print("mass: разбор не найден"); sys.exit(1)
s = s.replace(old2, new2)

old3 = """    top = [r for r in sorted(rows, key=lambda x: -x[1]) if r[1] > 0]"""
new3 = """    top = [r for r in sorted(rows, key=lambda x: -x[1]) if r[1] >= MIN and r[4]]"""
if s.count(old3) != 1:
    print("mass: топ не найден"); sys.exit(1)
s = s.replace(old3, new3)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("порог ок")
