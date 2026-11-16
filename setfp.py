import io, json, os, sys

D = r"C:\work\hunt2\data\vuln"
FP = {
    "CVE-2020-25213": ["inurl:/wp-content/plugins/wp-file-manager/"],
    "CVE-2020-11738": ["inurl:/wp-content/plugins/duplicator/"],
    "CVE-2023-6553": ["inurl:/wp-content/plugins/backup-backup/"],
}
for cve, fp in FP.items():
    p = os.path.join(D, cve, "vuln.json")
    if not os.path.isfile(p):
        print("нет", p); continue
    v = json.load(open(p, encoding="utf-8"))
    v["footprint"] = fp
    json.dump(v, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(cve, "ok")

P = r"C:\work\hunt2\core\discover.py"
L = io.open(P, encoding="utf-8").read().split("\n")
i0 = next((i for i, l in enumerate(L) if l.startswith("def _query(")), None)
i1 = next((i for i, l in enumerate(L) if l.startswith("def _links(")), None)
if i0 is None or i1 is None:
    print("_query не найден"); sys.exit(1)
L[i0:i1] = '''def _query(v):
    for line in v.get("footprint", []):
        if "inurl:" in line:
            return line.split("inurl:", 1)[1].strip().strip('"')
    plug = v.get("plugin")
    if plug:
        return "/wp-content/plugins/%s/" % plug
    return ""

'''.split("\n")
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("_query ok")