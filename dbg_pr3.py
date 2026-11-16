import traceback
from core import vuln

orig = vuln._exploit

def wrap(*a, **k):
    try:
        return orig(*a, **k)
    except Exception:
        traceback.print_exc()
        raise

vuln._exploit = wrap
v = vuln.load("CVE-2026-87902")
print(vuln.probe("www.selftherapie.com", v, 120, "PBLTEST123"))