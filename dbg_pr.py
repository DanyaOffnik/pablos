import traceback
from core import vuln
v = vuln.load("CVE-2026-87902")
try:
    r = vuln.probe("www.selftherapie.com", v, 120, "PBLTEST123")
    print(r)
except Exception:
    traceback.print_exc()