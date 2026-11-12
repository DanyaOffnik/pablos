# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\mass.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    if ui.ask("разложить списки (1 да / 0 нет)", "1") == "1":"""
new = """    ui.say("разложить: годные уйдут в разбор, мусор в мусор, очередь почистится")
    if ui.ask("разложить списки (1 да / 0 нет)", "1") == "1":"""
if s.count(old) != 1:
    print("mass: вопрос не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("mass ок")
