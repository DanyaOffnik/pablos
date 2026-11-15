import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = "def run(cve_id, hosts, threads=8, tmo=30, limit=0):\n    _STOP.clear()"
new = ("def run(cve_id, hosts, threads=8, tmo=30, limit=0, stop_fn=None):\n"
       "    _STOP.clear()\n\n"
       "    def _halt():\n"
       "        return _STOP.is_set() or (stop_fn is not None and stop_fn())\n")
if s.count(old) != 1:
    print("run() не найден"); sys.exit(1)
s = s.replace(old, new)

old = "        while not _STOP.is_set():"
new = "        while not _halt():"
if s.count(old) != 1:
    print("worker loop не найден"); sys.exit(1)
s = s.replace(old, new)

old = "def sources_file(path):"
new = ('''def append_list(cve_id, hosts):
    p = list_path(cve_id)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        for h in hosts:
            h = h.strip()
            if h:
                f.write(h + "\\n")


def list_count(cve_id):
    p = list_path(cve_id)
    if not os.path.isfile(p):
        return 0
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sum(1 for ln in f if ln.strip())


def sources_file(path):''')
if s.count(old) != 1:
    print("sources_file не найден"); sys.exit(1)
s = s.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("vuln.py ok")