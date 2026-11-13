# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
"""    if kind == "нет связи":
        st[host] = {"score": -2, "notes": ["нет связи"], "creds": "", "done": True,
                    "at": time.strftime("%Y-%m-%d %H:%M")}
        _DIRTY[0] = True
        return host, st[host]""",
"""    if kind == "нет связи":
        st[host] = {"score": -2, "notes": ["нет связи"], "creds": "", "done": True,
                    "at": time.strftime("%Y-%m-%d %H:%M")}
        _DIRTY[0] = True
        _append(host, st[host])
        return host, st[host]"""))

PAIRS.append((
"""        if not use_browser:
            st[host] = {"score": 0, "notes": ["защита"], "creds": "", "done": True,
                        "at": time.strftime("%Y-%m-%d %H:%M")}
            _DIRTY[0] = True
            return host, st[host]""",
"""        if not use_browser:
            st[host] = {"score": 0, "notes": ["защита"], "creds": "", "done": True,
                        "at": time.strftime("%Y-%m-%d %H:%M")}
            _DIRTY[0] = True
            _append(host, st[host])
            return host, st[host]"""))

PAIRS.append((
"""        if (_call(_blocked, 25, host)[1] or "") == "защита":
            st[host] = {"score": 0, "notes": ["защита не пройдена"], "creds": "",
                        "done": True, "at": time.strftime("%Y-%m-%d %H:%M")}
            _DIRTY[0] = True
            return host, st[host]""",
"""        if (_call(_blocked, 25, host)[1] or "") == "защита":
            st[host] = {"score": 0, "notes": ["защита не пройдена"], "creds": "",
                        "done": True, "at": time.strftime("%Y-%m-%d %H:%M")}
            _DIRTY[0] = True
            _append(host, st[host])
            return host, st[host]"""))

PAIRS.append((
"""    hits = [(h, r) for h, r in st.items() if r.get("creds")]""",
"""    hits = [(h, st.get(h) or {}) for h in left if (st.get(h) or {}).get("creds")]"""))

for i, (old, new) in enumerate(PAIRS, 1):
    if s.count(old) != 1:
        print("замена %d: найдено %d" % (i, s.count(old))); sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
