# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    hosts = only or queue.queue()
    if not hosts:
        ui.say("очередь пуста")
        return"""
new = """    hosts = list(only or [])
    if not hosts:
        try:
            from core import state as _state
            hosts = [d["host"] for d in _state.by_status("hot")]
        except Exception:
            hosts = []
        if not hosts:
            hosts = queue.queue()
    if not hosts:
        ui.say("очередь пуста")
        return"""
if s.count(old) != 1:
    print("night: старт не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("night ок")
