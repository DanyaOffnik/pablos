# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()

old = "from core import browser, config, hints, http, notify, queue, ui, waf"
new = "from core import browser, config, hints, http, notify, queue, state, ui, waf"
if s.count(old) != 1:
    print("night: импорт не найден"); sys.exit(1)
s = s.replace(old, new)

old2 = """    ui.say("отчёт: " + report)
    if os.path.isfile(ERRS):
        ui.say("ошибки: " + ERRS)"""
new2 = """    ui.say("отчёт: " + report)
    if os.path.isfile(ERRS):
        ui.say("ошибки: " + ERRS)

    for host in left:
        rec = st.get(host) or {}
        try:
            if rec.get("creds"):
                state.set_status(host, "cracked", note="вход", score=rec.get("score", 0))
            elif rec.get("score", 0) > 0:
                state.set_status(host, "scanned", note="отработано", score=rec.get("score", 0))
            else:
                state.set_status(host, "trash", note="пусто", score=rec.get("score", 0))
        except Exception:
            pass"""
if s.count(old2) != 1:
    print("night: отчёт не найден"); sys.exit(1)
s = s.replace(old2, new2)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("night ок")
