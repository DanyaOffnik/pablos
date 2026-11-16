import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = "    return False, last\n"
new = '    return False, last, ""\n'
if s.count(old) != 1:
    print("финальный return не найден, вхождений:", s.count(old)); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")