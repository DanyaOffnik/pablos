# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """        except KeyboardInterrupt:
            print()
            ui.warn("прервано")
            ui.pause()"""
new = """        except KeyboardInterrupt:
            print()
            ui.warn("прервано")
            ui.pause()
        except Exception:
            import traceback
            print()
            ui.err("сбой пункта, вернулся в меню")
            print(traceback.format_exc(limit=3))
            ui.pause()"""
if s.count(old) != 1:
    print("panel: main не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """    if c == "0" or not c.isdigit():
        return"""
new2 = """    if c == "0" or not c.isdigit():
        return
    if not runs:
        ui.say("прогонов нет")
        ui.pause()
        return"""
if s.count(old2) != 1:
    print("panel: do_reports не найдено"); sys.exit(1)
s = s.replace(old2, new2)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("panel ок")
