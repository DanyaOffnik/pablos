import urllib.parse, re
from core import http

for q in ["inurl:/wp-content/themes/twentyfourteen/",
          "inurl:/wp-content/themes/twentytwelve/",
          "inurl:wp-content/themes/twentyfourteen"]:
    p = "/search?q=" + urllib.parse.quote(q) + "&format=rss&count=50"
    http.drop("www.bing.com")
    r = http.request("www.bing.com", p, tries=1)
    t = r.text or ""
    links = re.findall(r"<item><title>.*?</title><link>([^<]+)</link>", t)
    hit = [u for u in links if "themes/twenty" in u]
    print(q, "| items:", len(links), "| с путём:", len(hit))
    for u in hit[:4]:
        print("   ", u[:100])