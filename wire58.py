# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """def tool_keep(h):"""
new = """def tool_passive(h):
    from modules import passive
    got = passive.run(h) or []
    ui.say("находок: %d" % len(got))


def tool_dumpfuzz(h):
    from modules import dumpfuzz
    got = dumpfuzz.run(h) or []
    ui.say("дампов: %d" % len(got))


def tool_sqli(h):
    from modules import extract, sqli
    got = sqli.run(h, _kind(h)) or []
    if not got:
        return
    ui.say("подтверждено: %d" % len(got))
    if ui.ask("разрабатывать (1 да / 0 нет)", "1") == "1":
        extract.run(h, got, True)


def tool_reg(h):
    from modules import reg
    got = reg.run(h, _kind(h)) or []
    ui.say("форм: %d" % len(got))


def tool_keep(h):"""
if s.count(old) != 1:
    print("panel: tool_keep не найден"); sys.exit(1)
s = s.replace(old, new)

old2 = """    ("10", "закрепление", tool_keep, "свой доступ"),
]"""
new2 = """    ("10", "пассивный сбор", tool_passive, "архив, сертификаты"),
    ("11", "поиск дампов", tool_dumpfuzz, "бэкапы по датам"),
    ("12", "инъекции", tool_sqli, "проверка и вывод"),
    ("13", "регистрация", tool_reg, "завести учётку"),
    ("14", "закрепление", tool_keep, "свой доступ"),
]"""
if s.count(old2) != 1:
    print("panel: TOOLS не найдены"); sys.exit(1)
s = s.replace(old2, new2)

old3 = """            try:
                night.run()
            except Exception:
                ui.err("упал:")
                print(traceback.format_exc())
            ui.pause()"""
new3 = """            try:
                night.run()
            except Exception:
                tb = traceback.format_exc()
                p = os.path.join(config.DATA, "last_error.log")
                try:
                    with open(p, "a", encoding="utf-8") as f:
                        f.write(tb + "\\n")
                except Exception:
                    pass
                ui.err("упал, текст в " + p)
                print(tb)
            ui.pause()"""
if s.count(old3) != 1:
    print("panel: ночной не найден"); sys.exit(1)
s = s.replace(old3, new3)

old4 = """        except Exception:
            import traceback
            print()
            ui.err("сбой пункта, вернулся в меню")
            print(traceback.format_exc(limit=3))
            ui.pause()"""
new4 = """        except Exception:
            import traceback
            tb = traceback.format_exc()
            p = os.path.join(config.DATA, "last_error.log")
            try:
                with open(p, "a", encoding="utf-8") as f:
                    f.write(tb + "\\n")
            except Exception:
                pass
            print()
            ui.err("сбой пункта, текст в " + p)
            print(tb)
            ui.pause()"""
if s.count(old4) != 1:
    print("panel: main не найден"); sys.exit(1)
s = s.replace(old4, new4)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("panel ок")
