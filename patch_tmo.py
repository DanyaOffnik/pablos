import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = "def run(cve_id, hosts, threads=8, tmo=30, limit=0, stop_fn=None):"
new = "def run(cve_id, hosts, threads=8, tmo=90, limit=0, stop_fn=None):"
if s.count(old) != 1:
    print("run не найден"); sys.exit(1)
s = s.replace(old, new)

old = '    r.add_argument("--timeout", type=int, default=30)'
if old not in s:
    pass
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("дедлайн 90")