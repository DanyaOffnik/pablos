import urllib.parse, re, time
from core import http

q = urllib.parse.quote("inurl:/wp-content/plugins/wp-file-manager/")
allu = []
for _ in range(10):
    http.drop("www.bing.com")
    r = http.request("www.bing.com", "/search?q=" + q + "&format=rss&count=50", tries=1)
    t = r.text or ""
    if "<item>" in t:
        allu += re.findall(r"<item><title>.*?</title><link>([^<]+)</link>", t)
        if len(allu) >= 20:
            break
    time.sleep(2)
print("собрано ссылок:", len(allu))
hit = [u for u in allu if "wp-file-manager" in u]
print("с путём:", len(hit))
for u in allu[:12]:
    print(("ДА " if "wp-file-manager" in u else "нет"), u[:100])