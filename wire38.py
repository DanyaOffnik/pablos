# -*- coding: utf-8 -*-
import io, sys
P = r"C:\work\hunt2\smoke.py"
s = io.open(P, encoding="utf-8-sig").read()
for old, new in (
 ('"modules.profiles", "modules.post",',
  '"modules.profiles", "modules.post", "modules.reg",'),
 ('    ("modules.extract", ("run", "_dbms", "_parse")),',
  '    ("modules.extract", ("run", "_dbms", "_parse")),\n    ("modules.reg", ("run", "PATHS")),')):
    if s.count(old) != 1:
        print("smoke: нет " + old[:35]); sys.exit(1)
    s = s.replace(old, new)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
print("smoke ок")
