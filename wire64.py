import io, sys

P = r"C:\work\hunt2\core\http.py"
src = io.open(P, encoding="utf-8").read()

OLD = "    px = proxy_for(host)\n"
NEW = ("    s.headers[\"Accept-Encoding\"] = \"gzip, deflate, br\"\n"
       "    px = proxy_for(host)\n")

if "Accept-Encoding" in src:
    print("уже пропатчено")
    sys.exit(0)

n = src.count(OLD)
print("вхождений px = proxy_for(host):", n)
if n != 1:
    print("НЕ ТО, правь вручную")
    sys.exit(1)

src = src.replace(OLD, NEW, 1)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("ok: Accept-Encoding добавлен в session()")

import py_compile
py_compile.compile(P, doraise=True)
print("компиляция ok")
