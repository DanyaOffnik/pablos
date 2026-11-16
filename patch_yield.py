import io, sys
P = r"C:\work\hunt2\core\discover.py"
L = io.open(P, encoding="utf-8").read().split("\n")

i0 = next((i for i, l in enumerate(L) if l.startswith("def _bing(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def _ddg(")), None)
if i0 is None or i1 is None:
    print("границы _bing не найдены"); sys.exit(1)

new = '''def _variants(q):
    q = q.strip("/")
    if not q:
        return []
    slug = q.rsplit("/", 1)[-1]
    out = ["/" + q + "/", "/" + q]
    if slug and slug not in out:
        out.append(slug)
    return out


def _bing(q, limit):
    got = set()
    for v in _variants(q):
        for page in range(0, 8):
            path = ("/search?q=" + urllib.parse.quote("inurl:" + v)
                    + "&format=rss&count=50&first=%d" % (page * 10 + 1))
            try:
                r = _get("www.bing.com", path)
            except Exception:
                break
            if getattr(r, "status_code", 0) != 200:
                break
            part = _clean({urllib.parse.urlparse(u).hostname
                           for u in _links(getattr(r, "text", ""))})
            if not part:
                break
            before = len(got)
            got |= part
            if len(got) >= limit:
                return got
            if len(got) == before and page > 2:
                break
            time.sleep(random.uniform(1.5, 3.0))
    return got

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_bing переписан")