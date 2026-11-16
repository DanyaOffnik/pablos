import re, urllib.parse
from core import http

base_q = "inurl:/wp-content/plugins/"
variants = [" site:.ru", " site:.by", " site:.kz", " site:.ua", " site:.md",
            " woocommerce", " wordpress", " контакты", " shop", " blog"]
for v in variants:
    q = base_q + v
    p = "/search?q=" + urllib.parse.quote(q) + "&format=rss&count=50"
    http.drop("www.bing.com")
    try:
        r = http.request("www.bing.com", p, tries=1)
    except Exception as e:
        print(v, "EXC", type(e).__name__); continue
    links = re.findall(r"<item><title>.*?</title><link>([^<]+)</link>", r.text or "")
    hosts = {urllib.parse.urlparse(u).hostname for u in links if "wp-content" in u}
    print("%-14s items=%d хостов=%d" % (v.strip() or "-", len(links), len(hosts)))