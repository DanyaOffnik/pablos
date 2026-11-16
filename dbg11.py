import urllib.parse, re
from core import http

q = urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/")
http.drop("www.bing.com")
r = http.request("www.bing.com", "/search?q=" + q + "&format=rss&count=50", tries=1)
t = r.text or ""
i = t.find("<item>")
print(t[i:i + 900])