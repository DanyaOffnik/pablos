import urllib.parse, time
from core import http

q = urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/")
for extra in ["", "&first=1", "&first=11", "&count=50&first=1"]:
    p = "/search?q=" + q + "&format=rss&count=50" + extra
    http.drop("www.bing.com")
    r = http.request("www.bing.com", p, tries=1)
    t = r.text or ""
    print("%-22s status %s items %d len %d" % (extra or "-", r.status_code, t.count("<item>"), len(t)))
    time.sleep(3)