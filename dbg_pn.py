from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"

def post(body):
    return vuln._req("POST", base + "/", body=body.encode(), ctype=CT)

cases = [
    ("pagename=o-nas",            "pagename=o-nas"),
    ("pagename=/o-nas/",          "pagename=%2Fo-nas%2F"),
    ("pagename=o-nas + page_id",  "pagename=o-nas&page_id=4473"),
    ("pagename пустой",           "pagename="),
    ("ничего",                    ""),
]
for name, body in cases:
    try:
        r = post(body)
    except Exception as e:
        print(name, "EXC", type(e).__name__); continue
    t = r.text or ""
    title = ""
    i = t.find("<title>")
    if i > 0:
        title = t[i + 7:i + 80].split("<")[0]
    print("%-28s %s len=%d title=%r" % (name, r.status_code, len(t), title[:50]))