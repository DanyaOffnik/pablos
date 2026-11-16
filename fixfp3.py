import json
p = r"C:\work\hunt2\data\vuln\CVE-2026-87902\vuln.json"
v = json.load(open(p, encoding="utf-8"))
v["footprint"] = ["inurl:/wp-content/plugins/"]
json.dump(v, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("ok")