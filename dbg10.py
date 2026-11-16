import urllib.parse, re
from core import http

q = urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/")
http.drop("www.bing.com")
r = http.request("www.bing.com", "/search?q=" + q + "&format=rss&count=50", tries=1)
for u in re.findall(r"<link>(https?://[^<]+)</link>", r.text or "")[1:11]:
    print(("ДА " if "wp-file-manager" in u else "нет") , u[:110])