import io, sys

P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()
L = s.split("\n")

starts = [i for i, l in enumerate(L) if l.strip() == "def do_run():"]
if len(starts) != 1:
    print("do_run не один:", len(starts)); sys.exit(1)
i0 = starts[0]
i1 = next((i for i in range(i0 + 1, len(L)) if L[i].startswith("def ")), len(L))
seg = L[i0:i1]

j = next((k for k, l in enumerate(seg) if "возобновить отложенные" in l), None)
if j is None:
    print("пункт 5 не найден внутри do_run"); sys.exit(1)
seg.insert(j + 2, '        ui.item("6", "поиск по дырам", "список доменов -> CVE -> эксплойт")')

k = next((x for x, l in enumerate(seg) if 'ui.ask("пункт")' in l), None)
if k is None:
    print("ввод пункта не найден"); sys.exit(1)
seg.insert(k + 1, '        if c == "6":\n            from modules import vulntab\n            vulntab.run()\n            continue')

L[i0:i1] = seg
io.open(P, "w", encoding="utf-8-sig", newline="\n").write("\n".join(L))
print("panel.py пропатчен")