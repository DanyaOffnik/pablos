import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """    rec["state"] = "confirmed"
    sink(dict(rec))

    try:"""
new = """    rec["state"] = "confirmed"
    sink(dict(rec))

    if not v.get("exploit", {}).get("url"):
        return rec

    try:"""
if s.count(old) != 1:
    print("место не найдено"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")