# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """    window = max(2, workers * 2)"""
new = """    window = workers + 1"""
if s.count(old) != 1:
    print("night: окно не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """    for h in left:
        st[h] = {"score": 0, "notes": [], "creds": "", "stage": "в очереди"}"""
new2 = """    for h in left:
        st[h] = {"score": 0, "notes": [], "creds": "", "stage": "в очереди"}
    for h in left[:window]:
        st[h]["stage"] = "взято в пул" """
if s.count(old2) != 1:
    print("night: заполнение не найдено"); sys.exit(1)
s = s.replace(old2, new2)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
