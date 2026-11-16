import urllib.parse, time
from core import http

p = "/search?q=" + urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/") + "&format=rss&count=50"
ok = 0
for i in range(10):
    http.drop("www.bing.com")
    try:
        r = http.request("www.bing.com", p, tries=1)
        n = (r.text or "").count("<item>")
    except Exception as e:
        n = -1
    ok += 1 if n > 0 else 0
    print(i, "items", n)
    time.sleep(2)
print("успешных из 10:", ok)