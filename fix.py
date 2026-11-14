import csv, re, sys
sys.path.insert(0, r"C:\work\hunt2")
from core import http

SRC = r"C:\work\manual\romis.by\products.csv"
OUT = r"C:\work\manual\romis.by\products_fixed.csv"

rows = list(csv.reader(open(SRC, encoding="utf-8", errors="ignore")))
head, body = rows[0], rows[1:]
print("строк:", len(body))

bad = [r for r in body if len(r) > 1 and not r[1].strip()]
print("битых на догон:", len(bad))

for r in bad:
    u = r[0]
    try:
        resp = http.get(host="romis.by", path=u.replace("https://romis.by", ""), timeout=30, tries=2)
        t = resp.text or "" if resp is not None else ""
    except Exception:
        t = ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    if m:
        r[1] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()[:200]
    m = re.search(r'itemprop="price"\s+content="([^"]*)"', t)
    if m:
        r[2] = m.group(1)
    m = re.search(r'itemprop="availability"\s+href="[^"]*schema\.org/(\w+)"', t)
    if m:
        r[3] = m.group(1)

ok = 0
for r in body:
    if len(r) < 6:
        r += [""] * (6 - len(r))
    name = r[1]
    m = re.search(r"\(([0-9A-Za-zА-Яа-я\-]{3,40})\)\s*$", name) or re.search(r"[,;]\s*([0-9A-Za-z\-]{4,40})\s*$", name)
    if m:
        r[4] = m.group(1)
    else:
        tail = r[0].rstrip("/").rsplit("-", 1)[-1]
        r[4] = tail if re.fullmatch(r"[0-9A-Za-z\-]{3,40}", tail or "") else ""
    if r[3] not in ("InStock", "OutOfStock", "PreOrder"):
        r[3] = "InStock" if r[2] else "OutOfStock"
    if r[1] and r[2]:
        ok += 1

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(head)
    w.writerows(body)
print("записей с названием и ценой:", ok, "->", OUT)
