# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\core\queue.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """def drop_hot(host, where="done"):
    drop(host, where)"""
new = """def drop_hot(host, where="done"):
    drop(host, where)


def add_hot(host):
    \"\"\"Пометить годным: из очереди в отработанные.\"\"\"
    drop(host, "done")"""
if s.count(old) != 1:
    print("queue: не найдено"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("add_hot добавлен")
