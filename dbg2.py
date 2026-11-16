import urllib.parse
from core import http

variants = [
    'inurl:"/wp-content/plugins/wp-file-manager/"',
    '"wp-content/plugins/wp-file-manager"',
    'wp-content/plugins/wp-file-manager',
]
for q in variants:
    p = "/search?q=" + urllib.parse.quote(q)
    try:
        r = http.request("www.bing.com", p, tries=1)
    except Exception as e:
        print(q, "EXC", type(e).__name__)
        continue
    t = r.text or ""
    print("%-50s status %s len %d b_algo %d captcha %d"
          % (q, r.status_code, len(t), t.count("b_algo"), t.count("captcha")))