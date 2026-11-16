import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = '    with open(p, "w", encoding="utf-8", newline="\\n") as f:\n        f.write("\\n".join(lines) + "\\n")\n    return p'
new = '    with open(p, "w", encoding="utf-8-sig", newline="\\n") as f:\n        f.write("\\n".join(lines) + "\\n")\n    return p'
if s.count(old) != 1:
    print("запись отчёта не найдена"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")