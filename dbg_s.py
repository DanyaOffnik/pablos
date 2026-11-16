import urllib.parse
from core import http
q = urllib.parse.quote('inurl:"/wp-content/plugins/wp-file-manager/"')
for name, h, p in [("lite", "lite.duckduckgo.com", "/lite/?q=" + q),
                   ("bing", "www.bing.com", "/search?q=" + q)]:
    try:
        r = http.request(h, p, tries=1)
    except Exception as e:
        print(name, "EXC", type(e).__name__)
        continue
    t = getattr(r, "text", "") or ""
    print(name, "status", getattr(r, "status_code", "?"), "len", len(t),
          "uddg", t.count("uddg="), "cite", t.count("<cite"), "anomaly", "anomaly" in t)