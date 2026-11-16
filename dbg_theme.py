import re
from core import http, vuln

for h in ["mirk154.ru", "mypets.kg", "gomeldrev.by"]:
    r = http.request(h, "/", tries=1)
    t = r.text or ""
    themes = sorted(set(re.findall(r"/wp-content/themes/([a-z0-9._-]+)/", t)))
    print(h, "темы:", themes)
    for th in themes:
        for d in ["page-templates", "page-template", "page-templates-full-width", "templates"]:
            try:
                x = http.request(h, "/wp-content/themes/%s/%s/" % (th, d), tries=1)
            except Exception as e:
                print("   ", th, d, "EXC", type(e).__name__); continue
            print("   ", th, d, "->", x.status_code, len(x.text or ""))