import io, sys
P = r"C:\work\hunt2\core\vuln.py"
s = io.open(P, encoding="utf-8").read()
n = 0

pairs = [
 ('        _req("POST", url, data=body, headers={"Content-Type": ctype})',
  '        _req("POST", url, body=body, ctype=ctype)'),
 ('        _req("POST", url, data=body, headers={"Content-Type": ex.get(\n            "content_type", "application/x-www-form-urlencoded")})',
  '        _req("POST", url, body=body, ctype=ex.get(\n            "content_type", "application/x-www-form-urlencoded"))'),
 ('        return _req("POST", base + "/", data=body, headers=hdr)',
  '        return _req("POST", base + "/", body=body, ctype=CT)'),
 ('                _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",\n                     data=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), headers=hdr)',
  '                _req("POST", base + "/?+config-create+/" + payload + "+" + out + ".php",\n                     body=("page_id=%d&pagename=%s" % (pid, _denc(incp))).encode(), ctype=CT)'),
 ('    hdr = {"Content-Type": "application/x-www-form-urlencoded"}',
  '    CT = "application/x-www-form-urlencoded"'),
]
for old, new in pairs:
    if s.count(old) != 1:
        print("не найдено:", old.split("\n")[0][:60], "| вхождений:", s.count(old)); sys.exit(1)
    s = s.replace(old, new)
    n += 1

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("заменено:", n)