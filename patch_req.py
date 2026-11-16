import io, sys
P = r"C:\work\hunt2\core\vuln.py"
L = io.open(P, encoding="utf-8").read().split("\n")
i0 = next((i for i, l in enumerate(L) if l.startswith("def _req(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def _rnd(")), None)
if i0 is None or i1 is None:
    print("границы _req не найдены"); sys.exit(1)

new = '''def _req(method, url, **kw):
    _left()
    kw.setdefault("tries", 1)
    if url.startswith("http"):
        from urllib.parse import urlsplit
        parts = urlsplit(url)
        host = parts.netloc
        path = (parts.path or "/") + (("?" + parts.query) if parts.query else "")
    else:
        host, path = url, "/"
    return http.request(host, path, method=method, **kw)

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_req исправлен")