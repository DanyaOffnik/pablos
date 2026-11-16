import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """    with open(p, "a", encoding="utf-8") as f:
        for h in hosts:"""
new = """    if os.path.isfile(p) and os.path.getsize(p):
        with open(p, "rb") as f:
            f.seek(-1, 2)
            if f.read(1) != b"\\n":
                with open(p, "a", encoding="utf-8") as g:
                    g.write("\\n")
    with open(p, "a", encoding="utf-8") as f:
        for h in hosts:"""
if s.count(old) != 1:
    print("append_list не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")