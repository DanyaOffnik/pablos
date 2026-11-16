import re, urllib.parse
from core import http

SKIP = ("bing.com", "google.com", "microsoft.com", "wordpress.org")
variants = [
    "inurl:wp-content/plugins/wp-file-manager",
    "inurl:/wp-content/plugins/wp-file-manager/",
    "inurl:wp-file-manager",
    'inurl:"wp-file-manager"',
]
for q in variants:
    p = "/search?q=" + urllib.parse.quote(q) + "&format=rss&count=50"
    r = http.request("www.bing.com", p, tries=1)
    t = r.text or ""
    hosts = {urllib.parse.urlparse(x).hostname for x in re.findall(r"<link>(https?://[^<]+)</link>", t)}
    hosts = {h for h in hosts if h and not any(h.endswith(s) for s in SKIP)}
    print("%-45s status %s items %d годных %d" % (q, r.status_code, len(hosts), len(hosts)))
    for h in list(hosts)[:6]:
        print("   ", h)