import io, sys
P = r"C:\work\hunt2\core\discover.py"
L = io.open(P, encoding="utf-8").read().split("\n")

i0 = next((i for i, l in enumerate(L) if l.startswith("def _bing(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def _ddg(")), None)
if i0 is None or i1 is None:
    print("границы _bing не найдены"); sys.exit(1)

new = '''def _page(q, page, attempts=3):
    path = ("/search?q=" + urllib.parse.quote("inurl:" + q)
            + "&format=rss&count=50&first=%d" % (page * 10 + 1))
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
        part = _clean({urllib.parse.urlparse(u).hostname
                       for u in _links(getattr(r, "text", ""))})
        if part:
            return part
        time.sleep(2.0)
    return set()


def _bing(q, limit):
    got = set()
    for v in _variants(q):
        for page in range(0, 6):
            part = _page(v, page)
            if not part:
                break
            before = len(got)
            got |= part
            if len(got) >= limit:
                return got
            if len(got) == before and page > 1:
                break
            time.sleep(random.uniform(1.2, 2.5))
    return got

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_bing с тремя попытками")