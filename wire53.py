# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """def _saver(stop):
    while not stop.wait(5):
        if _DIRTY[0]:
            _save(st)"""
new = """def _saver(stop, st):
    while not stop.wait(5):
        if _DIRTY[0]:
            _save(st)"""
if s.count(old) != 1:
    print("night: _saver не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """    threading.Thread(target=_saver, args=(stop,), daemon=True).start()"""
new2 = """    threading.Thread(target=_saver, args=(stop, st), daemon=True).start()"""
if s.count(old2) != 1:
    print("night: запуск _saver не найден"); sys.exit(1)
s = s.replace(old2, new2)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
