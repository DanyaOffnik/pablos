import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old1 = '                if re.search(r"(?i)(PEAR_|Commands:|config-create|PEAR.Config)", t1):\n                    return True, "lfi:pear " + inc, base + "/"'
new1 = '                pear = bool(re.search(r"(?i)(PEAR_|Commands:|config-create|PEAR.Config)", t1))'
if s.count(old1) != 1:
    print("проверка pear не найдена"); sys.exit(1)
s = s.replace(old1, new1)

old2 = '                r = post(outp)'
new2 = ('                r = post(outp)\n'
        '                if marker in (getattr(r, "text", "") or ""):\n'
        '                    return True, "lfi:rce %s depth %d %s" % (td, depth, inc), base + "/"\n'
        '                if pear:\n'
        '                    return True, "lfi:pear " + inc, base + "/"')
if s.count(old2) != 1:
    print("вызов stage2 не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old2, new2))
print("ok")