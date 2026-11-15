import io, sys
P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """        ui.item("5", "возобновить отложенные", "капча, лимит, блок")
        ui.item("0", "назад")"""
new = """        ui.item("5", "возобновить отложенные", "капча, лимит, блок")
        ui.item("6", "поиск по дырам", "список доменов -> CVE -> эксплойт")
        ui.item("0", "назад")"""
if s.count(old) != 1:
    print("меню не найдено"); sys.exit(1)
s = s.replace(old, new)

old = """        c = ui.ask("пункт")
        if c == "0":
            return"""
new = """        c = ui.ask("пункт")
        if c == "0":
            return
        if c == "6":
            from modules import vulntab
            vulntab.run()
            continue"""
if s.count(old) != 1:
    print("ветка пункта не найдена"); sys.exit(1)
s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
print("panel.py ok")