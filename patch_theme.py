import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = """    pid = _find_page(base)
    if not pid:
        return False, "lfi:no-page", \"\""""
new = """    try:
        hr = _req("GET", base + "/")
        html = getattr(hr, "text", "") or ""
    except Exception:
        html = ""
    themes = set(re.findall(r"/wp-content/themes/([a-z0-9._-]+)/", html))
    allow = ex.get("themes") or []
    if allow and themes and not (themes & set(allow)):
        return False, "lfi:theme " + ",".join(sorted(themes))[:40], ""

    pid = _find_page(base)
    if not pid:
        return False, "lfi:no-page", \"\""""
if s.count(old) != 1:
    print("шапка _wp_lfi не найдена"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")