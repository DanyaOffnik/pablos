import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = "            if t and abs(len(t) - base_len) > base_len * 0.2:"
new = "            if t and abs(len(t) - base_len) > base_len * 0.05:"
if s.count(old) != 1:
    print("порог не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("порог 5%")