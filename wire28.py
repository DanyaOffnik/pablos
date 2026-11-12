# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\tplui.py"
s = io.open(P, encoding="utf-8-sig").read()
old = 'TPL = os.path.join(config.DATA, "templates")'
new = "TPL = config.TPL"
if s.count(old) != 1:
    print("tplui: путь не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)
print("tplui: путь исправлен")
