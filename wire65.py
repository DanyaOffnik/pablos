import io, sys, py_compile

P = r"C:\work\hunt2\core\http.py"
src = io.open(P, encoding="utf-8").read()

if "_dec(" in src:
    print("уже пропатчено")
    sys.exit(0)

HELPER = '''
def _dec(r):
    enc = (r.headers.get("content-encoding") or "").lower()
    if not enc or not r.content:
        return r
    try:
        raw = r.content
        if enc == "zstd":
            import zstandard
            with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)) as rd:
                raw = rd.read()
        elif enc == "br":
            import brotli
            raw = brotli.decompress(raw)
        elif enc == "deflate":
            raw = zlib.decompress(raw)
        else:
            return r
        r._content = raw
        r.headers["content-encoding"] = "identity"
    except Exception:
        pass
    return r


'''

A1 = "def _bad(px):\n"
A2 = "        last_r = r\n"

if src.count(A1) != 1 or src.count(A2) != 1:
    print("якоря не совпали:", src.count(A1), src.count(A2))
    sys.exit(1)

src = src.replace("import os\n", "import io\nimport os\n", 1)
src = src.replace(A1, HELPER.lstrip("\n") + A1, 1)
src = src.replace(A2, A2 + "        _dec(r)\n", 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(src)
py_compile.compile(P, doraise=True)
print("ok: zstd/br/deflate распаковка вставлена, компиляция ok")
