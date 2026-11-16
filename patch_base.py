import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """    rx = ex.get("success_regex", "")
    last = ""
    for u in ex.get("urls") or [ex["url"]]:"""
new = """    rx = ex.get("success_regex", "")
    base404 = 0
    try:
        br = _req("GET", base + "/pbl-missing-" + rnd + ".php")
        base404 = len(getattr(br, "text", "") or "")
    except Exception:
        pass
    last = ""
    for u in ex.get("urls") or [ex["url"]]:"""
if s.count(old) != 1:
    print("шапка не найдена"); sys.exit(1)
s = s.replace(old, new)

old = """        for m in re.finditer(rx, text):
            tail = text[m.end():m.end() + 400]
            if "sourceURL" not in tail[:120] and "language_urls" not in text[max(0, m.start() - 200):m.start()]:
                return True, last, base + u"""
new = """        for m in re.finditer(rx, text):
            tail = text[m.end():m.end() + 400]
            if "sourceURL" not in tail[:120] and "language_urls" not in text[max(0, m.start() - 200):m.start()]:
                return True, last, base + u
        if base404 and abs(len(text) - base404) > base404 * 0.05:
            return True, last + " (отличается от 404)", base + u"""
if s.count(old) != 1:
    print("цикл не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")