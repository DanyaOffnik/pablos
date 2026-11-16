import re, urllib.parse
from core import http

for q in ['"wp-content/plugins/wp-file-manager"', 'wp-content/plugins/wp-file-manager']:
    p = "/search?q=" + urllib.parse.quote(q) + "&format=rss&count=50"
    r = http.request("www.bing.com", p, tries=1)
    t = r.text or ""
    links = re.findall(r"<link>(https?://[^<]+)</link>", t)
    hosts = {urllib.parse.urlparse(x).hostname for x in links}
    print("%-45s status %s len %d items %d hosts %d"
          % (q, r.status_code, len(t), len(links), len(hosts)))
    for h in list(hosts)[:5]:
        print("   ", h)