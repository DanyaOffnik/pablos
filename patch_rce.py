import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """                if re.search(r"(?i)(PEAR_|Commands:|config-create|PEAR.Config)", t1):
                    return True, "lfi:pear " + inc, base + "/"
                r = post(outp)"""
new = """                pear = bool(re.search(r"(?i)(PEAR_|Commands:|config-create|PEAR.Config)", t1))
                r = post(outp)
                if marker in (getattr(r, "text", "") or ""):
                    return True, "lfi:rce %s depth %d %s" % (td, depth, inc), base + "/"
                if pear:
                    return True, "lfi:pear " + inc, base + "/""""
if s.count(old) != 1:
    print("блок не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")