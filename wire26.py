# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\modules\brute.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
"from core import config, http, learn, ui, users, vault, verify",
"from core import config, http, learn, ui, users, vault, verify, waf"))

PAIRS.append((
"""    prof = profiles.get(kind) or {}
    sess = http.persist(host)""",
"""    prof = profiles.get(kind) or {}
    guard = (waf.known(host) or {}).get("strategy")
    if guard == "wait":
        pause = max(pause, 2.0)
    elif guard == "browser":
        pause = max(pause, 1.0)
    sess = http.persist(host)"""))

for i, (old, new) in enumerate(PAIRS, 1):
    n = s.count(old)
    if n != 1:
        print("ЗАМЕНА %d: найдено %d, стоп" % (i, n))
        sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("темп: ок")
