import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = """    with open(p, "a", encoding="utf-8") as f:
        for h in hosts:
            h = h.strip()
            if h:
                f.write(h + "\\n")"""
new = """    have = set()
    if os.path.isfile(p):
        with open(p, encoding="utf-8", errors="ignore") as g:
            have = {ln.strip().lower() for ln in g if ln.strip()}
    with open(p, "a", encoding="utf-8") as f:
        for h in hosts:
            h = h.strip()
            if h and h.lower() not in have:
                have.add(h.lower())
                f.write(h + "\\n")"""
if s.count(old) != 1:
    print("append_list не найден"); sys.exit(1)
s = s.replace(old, new)

old = "    queue = [h for h in hosts if h and h not in done]"
new = """    seen_q = set()
    queue = []
    for h in hosts:
        if h and h not in done and h not in seen_q:
            seen_q.add(h)
            queue.append(h)"""
if s.count(old) != 1:
    print("очередь не найдена"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")