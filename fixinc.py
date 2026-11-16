import json
p = r"C:\work\hunt2\data\vuln\CVE-2026-87902\vuln.json"
v = json.load(open(p, encoding="utf-8"))
v["exploit"]["includes"] = [
    "/usr/local/lib/php/pearcmd", "/usr/share/php/pearcmd", "/usr/lib/php/pearcmd",
    "/usr/share/pear/pearcmd", "/usr/local/pear/pearcmd", "/usr/share/php/PEAR/pearcmd",
    "/usr/lib/php5/pearcmd", "/usr/local/lib/pear/pearcmd", "/opt/pear/pearcmd",
    "/usr/local/share/pear/pearcmd", "/usr/share/php7/pearcmd", "/usr/share/php8/pearcmd"
]
json.dump(v, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("путей:", len(v["exploit"]["includes"]))