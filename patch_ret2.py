import io, sys
P = r"C:\work\hunt2\core\vuln.py"
L = io.open(P, encoding="utf-8").read().split("\n")
hit = [i for i, l in enumerate(L) if l.strip() == "return False, last,"]
if len(hit) != 1:
    print("вхождений:", len(hit)); sys.exit(1)
L[hit[0]] = '    return False, last, ""'
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("строка", hit[0] + 1, "исправлена")