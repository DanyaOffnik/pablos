import urllib.parse, re, time
from core import http

q = urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/")
t = ""
for _ in range(8):
    http.drop("www.bing.com")
    r = http.request("www.bing.com", "/search?q=" + q + "&format=rss&count=50", tries=1)
    t = r.text or ""
    if "<item>" in t:
        break
    time.sleep(2)
print("items:", t.count("<item>"))
i = t.find("<item>")
print(t[i:i + 700])