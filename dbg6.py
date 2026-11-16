import urllib.parse
from core import http

p = ("/search?q=" + urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/")
     + "&format=rss&count=50")
http.drop("www.bing.com")
r = http.request("www.bing.com", p, tries=1)
t = r.text or ""
print("status", r.status_code, "len", len(t), "items", t.count("<item>"))
print(t[:600])