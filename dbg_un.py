from core import vuln
v = vuln.load("CVE-2026-87902")

orig = vuln._exploit
vuln._exploit = lambda *a, **k: orig(*a, **k)
print("подмена активна:", vuln._exploit is not orig)

r = vuln._exploit("https://www.selftherapie.com", v["exploit"], "PBLTEST123")
print("тип:", type(r), "значение:", r)
try:
    a, b, c = r
    print("распаковка ok")
except Exception as e:
    print("распаковка падает:", type(e).__name__, e)