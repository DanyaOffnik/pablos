import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """def _affected(version, rule):
    c = _vcmp(version, rule.get("version", "0"))"""
new = """def _affected(version, rule):
    for lo, hi in rule.get("ranges") or []:
        if _vcmp(version, lo) >= 0 and _vcmp(version, hi) <= 0:
            return True
    if rule.get("ranges"):
        return False
    c = _vcmp(version, rule.get("version", "0"))"""
if s.count(old) != 1:
    print("_affected не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("диапазоны поддержаны")