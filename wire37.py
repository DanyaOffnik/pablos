# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """def tool_keep(h):"""
new = """def tool_reg(h):
    from modules import reg
    got = reg.run(h, _kind(h)) or []
    ui.say("форм: %d" % len(got))


def tool_keep(h):"""
if s.count(old) != 1:
    print("panel: не найдено"); sys.exit(1)
s = s.replace(old, new)
old2 = """    ("13", "закрепление", tool_keep, "свой доступ"),"""
new2 = """    ("13", "регистрация", tool_reg, "завести учётку"),
    ("14", "закрепление", tool_keep, "свой доступ"),"""
if s.count(old2) != 1:
    print("panel: TOOLS не найдено"); sys.exit(1)
s = s.replace(old2, new2)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("panel ок")
