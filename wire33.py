# -*- coding: utf-8 -*-
import io, sys
P = r"C:\work\hunt2\smoke.py"
s = io.open(P, encoding="utf-8-sig").read()
for old, new in (
 ('"modules.dossier", "modules.dumpfuzz", "modules.engine",',
  '"modules.dossier", "modules.dumpfuzz", "modules.engine", "modules.extract",'),
 ('    ("modules.dumpfuzz", ("run", "_names")),',
  '    ("modules.dumpfuzz", ("run", "_names")),\n    ("modules.extract", ("run", "_dbms", "_parse")),')):
    if s.count(old) != 1:
        print("smoke: нет " + old[:35]); sys.exit(1)
    s = s.replace(old, new)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
print("smoke ок")
