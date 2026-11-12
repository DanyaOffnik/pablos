# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """        ui.item("7", "картинка", "вкл / выкл")"""
new = """        ui.item("7", "картинка", "вкл / выкл")
        ui.item("8", "уровень уведомлений", "1 лом / 2 важное / 3 всё")"""
if s.count(old) != 1:
    print("panel: пункт не найден"); sys.exit(1)
s = s.replace(old, new)
old2 = """        elif ch == "7":
            notify.save_cfg({"tg_photo": not c.get("tg_photo", True)})
            ui.pause()"""
new2 = """        elif ch == "7":
            notify.save_cfg({"tg_photo": not c.get("tg_photo", True)})
            ui.pause()
        elif ch == "8":
            ui.say("сейчас: %d" % notify.level())
            v = ui.ask("порог 1/2/3 (1 только лом, 3 всё)", str(notify.level()))
            try:
                notify.save_cfg({"tg_level": max(1, min(3, int(v)))})
                ui.ok("порог: %d" % notify.level())
            except Exception:
                ui.err("нужно число")
            ui.pause()"""
if s.count(old2) != 1:
    print("panel: обработчик не найден"); sys.exit(1)
s = s.replace(old2, new2)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("panel ок")
