import urllib.parse
from core import http

q = '"wp-content/plugins/wp-file-manager"'
for i in range(4):
    p = "/search?q=" + urllib.parse.quote(q)
    r = http.request("www.bing.com", p, tries=1)
    t = r.text or ""
    print(i, "len", len(t), "b_algo", t.count("b_algo"), "b_results", t.count("b_results"),
          "h2a", t.count("<h2><a"), "nores", t.count("b_no"), "algo", t.count("b_alg"))
    if t.count("b_algo") == 0 and i == 0:
        import re
        print("--- фрагмент ---")
        print(re.sub(r"\s+", " ", t[3000:6000]))
    http.drop("www.bing.com")