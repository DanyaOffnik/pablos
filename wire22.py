# -*- coding: utf-8 -*-
import io, sys
P = r"C:\work\hunt2\smoke.py"
s = io.open(P, encoding="utf-8-sig").read()
for old, new in (
 ('"core.learn", "core.stack", "core.brfetch",',
  '"core.learn", "core.stack", "core.brfetch", "core.vault", "core.verify",'),
 ('"modules.profiles", "modules.recon",',
  '"modules.profiles", "modules.post", "modules.recon",'),
 ('    ("core.waf", ("detect", "known")),',
  '    ("core.waf", ("detect", "known")),\n    ("core.vault", ("add", "pairs")),\n    ("core.verify", ("confirm",)),\n    ("modules.post", ("run",)),')):
    if s.count(old) != 1:
        print("smoke: не найдено -> " + old[:40]); sys.exit(1)
    s = s.replace(old, new)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
print("smoke ок")
