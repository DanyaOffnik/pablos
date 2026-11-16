import io, sys
P = r"C:\work\hunt2\core\vuln.py"
L = io.open(P, encoding="utf-8").read().split("\n")
i0 = next((i for i, l in enumerate(L) if l.startswith("def _find_page(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def _wp_lfi(")), None)
if i0 is None or i1 is None:
    print("границы не найдены"); sys.exit(1)

new = '''def _find_page(base):
    for route in ("/wp-json/wp/v2/pages?per_page=100&_fields=id,slug,template",
                  "/index.php?rest_route=/wp/v2/pages&per_page=100&_fields=id,slug,template"):
        try:
            r = _req("GET", base + route)
            data = json.loads(getattr(r, "text", "[]"))
        except Exception:
            continue
        if isinstance(data, list) and data:
            for p in data:
                if not p.get("template"):
                    return p.get("id")
            return data[0].get("id")

    for sm in ("/wp-sitemap-posts-page-1.xml", "/sitemap.xml", "/page-sitemap.xml"):
        try:
            r = _req("GET", base + sm)
        except Exception:
            continue
        if getattr(r, "status_code", 0) != 200:
            continue
        for loc in re.findall(r"<loc>([^<]+)</loc>", getattr(r, "text", "") or ""):
            if "/wp-content/" in loc or loc.rstrip("/") == base.rstrip("/"):
                continue
            try:
                pr = _req("GET", loc)
            except Exception:
                continue
            m = re.search(r"page-id-(\\d+)", getattr(pr, "text", "") or "")
            if m:
                return int(m.group(1))
    return None

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_find_page с fallback")