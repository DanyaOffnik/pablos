import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = "def grab(cve_id):"
new = '''def report(cve_id):
    v = load(cve_id)
    rows = [r for r in _read_jsonl(sink_path(cve_id)) if r.get("state") in ("confirmed", "owned")]
    uniq = {}
    for r in rows:
        uniq.setdefault(r["host"], r)
    if not uniq:
        return ""
    p = os.path.join(DB, cve_id, "report.txt")
    lines = []
    lines.append("ОТЧЁТ ПО УЯЗВИМОСТИ")
    lines.append("=" * 60)
    lines.append("CVE:      " + v["id"])
    lines.append("Название: " + v.get("title", ""))
    lines.append("Диапазон: " + json.dumps(v.get("affected", {}), ensure_ascii=False))
    lines.append("Проверено хостов: %d, подтверждено: %d" % (len(seen(cve_id)) + len(uniq), len(uniq)))
    lines.append("")
    lines.append("%-40s %-10s %s" % ("хост", "версия", "статус"))
    lines.append("-" * 60)
    for h, r in sorted(uniq.items()):
        st = "шелл получен" if r.get("state") == "owned" else "уязвим по версии"
        lines.append("%-40s %-10s %s" % (h[:40], r.get("version", "-"), st))
    lines.append("")
    lines.append("Рекомендация: обновить WordPress до исправленной версии ветки.")
    with open(p, "w", encoding="utf-8", newline="\\n") as f:
        f.write("\\n".join(lines) + "\\n")
    return p


def grab(cve_id):'''
if s.count(old) != 1:
    print("grab не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))

P2 = r"C:\work\hunt2\vuln.py"
t = io.open(P2, encoding="utf-8").read()
old2 = '    g = sub.add_parser("grab")'
new2 = '    rp = sub.add_parser("report")\n    rp.add_argument("--cve", required=True)\n\n    g = sub.add_parser("grab")'
if t.count(old2) != 1:
    print("CLI не найден"); sys.exit(1)
t = t.replace(old2, new2)
old3 = '    if a.cmd == "grab":'
new3 = ('    if a.cmd == "report":\n'
        '        p = vuln.report(a.cve)\n'
        '        print(p or "нечего включать в отчёт")\n'
        '        return\n\n'
        '    if a.cmd == "grab":')
if t.count(old3) != 1:
    print("ветка grab не найдена"); sys.exit(1)
io.open(P2, "w", encoding="utf-8", newline="\n").write(t.replace(old3, new3))
print("ok")