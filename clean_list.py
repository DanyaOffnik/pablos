import re
p = r"C:\work\hunt2\data\vuln\CVE-2026-87902\list.txt"
t = open(p, encoding="utf-8", errors="ignore").read()
out = []
for m in re.finditer(r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,24}", t.lower()):
    h = m.group(0)
    if h.endswith(".php") or h.endswith(".xml"):
        continue
    out.append(h)
out = sorted(set(out))
open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("хостов:", len(out))