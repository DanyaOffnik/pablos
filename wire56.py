# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
"""    except Exception:
        _log("%s сбой: %s" % (host, traceback.format_exc().replace("\\n", " | ")[:300]))
        rec = st.get(host) or {}
        rec.setdefault("notes", []).append("сбой")
        rec["done"] = True
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        st[host] = rec
        _DIRTY[0] = True
        return host, rec""",
"""    except Exception:
        _log("%s сбой: %s" % (host, traceback.format_exc().replace("\\n", " | ")[:300]))
        rec = st.get(host) or {}
        rec.setdefault("notes", []).append("сбой")
        rec["done"] = True
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        st[host] = rec
        _DIRTY[0] = True
        try:
            _append(host, rec)
            queue.drop(host, "done")
        except Exception:
            pass
        return host, rec"""))

PAIRS.append((
"""                hits = _call(adminfind.run, 300, host, 16, None, kind)[1] or []""",
"""                hits = _call(adminfind.run, 320, host, 16, None, kind)[1] or []"""))

for i, (old, new) in enumerate(PAIRS, 1):
    if s.count(old) != 1:
        print("замена %d: найдено %d" % (i, s.count(old))); sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
