import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """        last = "traversal status:%s len:%d" % (getattr(r, "status_code", 0), len(text))
        if rx and re.search(rx, text):
            return True, last, base + u"""
new = """        last = "traversal status:%s len:%d" % (getattr(r, "status_code", 0), len(text))
        if not rx:
            continue
        for m in re.finditer(rx, text):
            tail = text[m.end():m.end() + 400]
            if "sourceURL" not in tail[:120] and "language_urls" not in text[max(0, m.start() - 200):m.start()]:
                return True, last, base + u"""
if s.count(old) != 1:
    print("блок не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")