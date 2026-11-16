from core import http
u = 'https://html.duckduckgo.com/html/?q=' + __import__('urllib.parse').parse.quote('inurl:"/wp-content/plugins/wp-file-manager/"')
try:
    r = http.request("GET", u, tries=1)
except TypeError as e:
    print("TypeError:", e)
    r = http.request("GET", u)
except Exception as e:
    print("EXC:", type(e).__name__, e)
    raise SystemExit
print("status:", getattr(r, "status_code", "?"), "len:", len(getattr(r, "text", "") or ""))
print((getattr(r, "text", "") or "")[:400])