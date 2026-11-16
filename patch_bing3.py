import io, sys
P = r"C:\work\hunt2\core\discover.py"
L = io.open(P, encoding="utf-8").read().split("\n")

i0 = next((i for i, l in enumerate(L) if l.startswith("def _page(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def _bing(")), None)
if i0 is None or i1 is None:
    print("границы _page не найдены"); sys.exit(1)

new = '''def _page(q, page, attempts=8):
    path = ("/search?q=" + urllib.parse.quote("inurl:" + q)
            + "&format=rss&count=50&first=%d" % (page * 10 + 1))
    slug = q.strip("/").rsplit("/", 1)[-1]
    for _ in range(attempts):
        http.drop("www.bing.com")
        try:
            r = _get("www.bing.com", path)
        except Exception:
            time.sleep(2.0)
            continue
        if getattr(r, "status_code", 0) != 200:
            time.sleep(2.0)
            continue
        links = _links(getattr(r, "text", ""))
        hit = {urllib.parse.urlparse(u).hostname for u in links
               if slug and slug in u}
        hit = _clean(hit)
        if hit:
            return hit
        time.sleep(2.0)
    return set()

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_page с постфильтром")