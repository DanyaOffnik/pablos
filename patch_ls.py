import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
old = """    good = []
    for td in ex.get("theme_dirs", ["page-templates"]):"""
new = """    dirs = list(ex.get("theme_dirs", ["page-templates"]))
    try:
        ls = _req("GET", base + "/wp-content/themes/" + theme + "/")
        if getattr(ls, "status_code", 0) == 200:
            found = sorted({d for d in re.findall(r"\\b(page-[a-z0-9._-]+)/", getattr(ls, "text", "") or "")})
            if found:
                dirs = found
    except Exception:
        pass

    good = []
    for td in dirs:"""
if s.count(old) != 1:
    print("цикл каталогов не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("листинг темы подключён")