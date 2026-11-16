from core import http
for h, th in [("leonidoff.by", "leoni"), ("mypets.kg", "flatsome"),
              ("www.selftherapie.com", "page-builder-framework")]:
    for p in ["/wp-content/themes/%s/style.css" % th, "/wp-content/themes/%s/" % th]:
        try:
            r = http.request(h, p, tries=1)
        except Exception as e:
            print(h, p, "EXC", type(e).__name__); continue
        print(h, p, "->", r.status_code, len(r.text or ""))