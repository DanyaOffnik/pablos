import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = '    if not v.get("exploit", {}).get("url"):\n        return rec'
new = ('    _ex = v.get("exploit") or {}\n'
       '    if not _ex or not (_ex.get("url") or _ex.get("type") == "wp_template_lfi"):\n'
       '        return rec')
if s.count(old) != 1:
    print("guard не найден"); sys.exit(1)
s = s.replace(old, new)

old = '    rnd = _rnd(8)\n    url = base + ex["url"]\n    kind = ex.get("type", "get_traversal")'
new = '    rnd = _rnd(8)\n    kind = ex.get("type", "get_traversal")\n    url = base + ex["url"] if ex.get("url") else base'
if s.count(old) != 1:
    print("шапка _exploit не найдена"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")