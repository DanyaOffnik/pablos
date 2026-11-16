import io, sys
P = r"C:\work\hunt2\modules\vulntab.py"
s = io.open(P, encoding="utf-8").read()

old = "def _footprint(ui):"
new = '''def _auto(ui):
    n = ui.ask("сколько хостов искать") or "50"
    n = int(n)
    ui.clear()
    ui.head("ПОИСК", "ищу по footprint, %d" % n)
    from core import discover
    got = discover.collect(S["cve"], n)
    got = [h for h in got if h not in vuln.seen(S["cve"])]
    if not got:
        ui.say("ничего не нашлось")
        ui.pause()
        return
    vuln.append_list(S["cve"], got)
    ui.ok("добавлено %d, стартую" % len(got))
    ui.pause()
    _start(ui)


def _footprint(ui):'''
if s.count(old) != 1:
    print("_footprint не найден"); sys.exit(1)
s = s.replace(old, new)

old = '        elif c == "f":'
new = '        elif c == "a":\n            _auto(ui)\n        elif c == "f":'
if s.count(old) != 1:
    print("ветка f не найдена"); sys.exit(1)
s = s.replace(old, new)

old = '        ui.item("v", "вставить домены", "")'
new = '        ui.item("a", "найти хосты сам", "")\n        ui.item("v", "вставить домены", "")'
if s.count(old) != 1:
    print("пункт v не найден"); sys.exit(1)
s = s.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("vulntab.py ok")