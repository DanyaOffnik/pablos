import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """    r = _req("GET", url)
    text = getattr(r, "text", "") or ""
    rx = ex.get("success_regex", "")
    hit = bool(rx) and re.search(rx, text) is not None
    return hit, "traversal status:%s len:%d" % (getattr(r, "status_code", 0), len(text)), url"""
new = """    rx = ex.get("success_regex", "")
    last = ""
    for u in ex.get("urls") or [ex["url"]]:
        r = _req("GET", base + u)
        text = getattr(r, "text", "") or ""
        last = "traversal status:%s len:%d" % (getattr(r, "status_code", 0), len(text))
        if rx and re.search(rx, text):
            return True, last, base + u
    return False, last, """""
if s.count(old) != 1:
    print("блок не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")