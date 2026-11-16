from core import http

dirs = ["page-templates", "page-template", "page-templates-full-width", "templates"]
files = ["full-width.php", "page-full-width.php", "template-full-width.php", "blank.php",
         "template-blank.php", "page-blank.php", "index.php", "header.php"]

for h, th in [("leonidoff.by", "leoni"), ("mypets.kg", "flatsome"),
              ("www.selftherapie.com", "page-builder-framework")]:
    print("==", h, th)
    for d in dirs:
        hits = []
        for f in files:
            try:
                r = http.request(h, "/wp-content/themes/%s/%s/%s" % (th, d, f), tries=1)
            except Exception:
                continue
            if r.status_code == 200:
                hits.append(f)
        if hits:
            print("   ", d, "->", hits)