import io, json
p = r"C:\work\hunt2\data\vuln\CVE-2026-87902\vuln.json"
v = json.load(open(p, encoding="utf-8"))
v["exploit"]["success_regex"] = "(?i)(PEAR_|Usage: pear|pear\\s+\\[options\\]|Commands:\\s*\\n\\s*(build|channel|config)|Cannot find PEAR)"
json.dump(v, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(v["exploit"]["success_regex"])