# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\core\notify.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """def hello_text():"""
new = """def level():
    \"\"\"Порог: 1 только лом, 2 важное, 3 всё подряд.\"\"\"
    try:
        return int(cfg().get("tg_level", 2))
    except Exception:
        return 2


def send_lvl(lvl, text):
    if lvl > level():
        return False
    return send(text)


def hello_text():"""
if s.count(old) != 1:
    print("notify: не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """def site(host, rec):
    v = verdict(rec)
    if not v:
        return False
    c = cfg()
    if not c.get("tg_sites", True):
        return False"""
new2 = """def site(host, rec):
    v = verdict(rec)
    if not v:
        return False
    c = cfg()
    if not c.get("tg_sites", True):
        return False
    lvl = 1 if rec.get("creds") else (2 if rec.get("score", 0) >= 8 else 3)
    if lvl > level():
        return False"""
if s.count(old2) != 1:
    print("notify: site не найдено"); sys.exit(1)
s = s.replace(old2, new2)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)

P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = [
 ('notify.send("ПОДДОМЕНЫ\\n%s\\n%s" % (host, ", ".join(sd[:5])))',
  'notify.send_lvl(3, "ПОДДОМЕНЫ\\n%s\\n%s" % (host, ", ".join(sd[:5])))'),
 ('''            loud = [(i, p) for i, p, c in th if c >= 6]
            if loud:
                notify.send("ЗАЦЕПКИ\\n%s\\n%s" % (host, "\\n".join("%s: %s" % (i, p[:40]) for i, p in loud[:4])))''',
  '''            loud = [(i, p, c) for i, p, c in th if c >= 6]
            if loud:
                lvl = 2 if max(c for _, _, c in loud) >= 8 else 3
                notify.send_lvl(lvl, "ЗАЦЕПКИ\\n%s\\n%s" % (
                    host, "\\n".join("%s: %s" % (i, p[:40]) for i, p, _ in loud[:4])))'''),
 ('notify.send("КРЕДЫ\\n%s\\n%s" % (host, res))',
  'notify.send_lvl(2, "КРЕДЫ\\n%s\\n%s" % (host, res))'),
 ('notify.send("ИНЪЕКЦИЯ\\n%s\\n%s" % (host, loud[0]["extra"]))',
  'notify.send_lvl(2, "ИНЪЕКЦИЯ\\n%s\\n%s" % (host, loud[0]["extra"]))'),
 ('notify.send("АРХИВ\\n%s\\n%s" % (host, ah[0][0]))',
  'notify.send_lvl(3, "АРХИВ\\n%s\\n%s" % (host, ah[0][0]))'),
 ('notify.send("ВХОД\\n%s\\n%s\\n%s" % (host, creds, kind))',
  'notify.send_lvl(1, "ВХОД\\n%s\\n%s\\n%s" % (host, creds, kind))'),
 ('notify.send("ПОВТОР ПАРОЛЯ\\n%s\\n%s" % (host, ", ".join(rp)))',
  'notify.send_lvl(2, "ПОВТОР ПАРОЛЯ\\n%s\\n%s" % (host, ", ".join(rp)))'),
 ('notify.send("СЛИВ %s: %s контактов" % (host, n))',
  'notify.send_lvl(1, "СЛИВ %s: %s контактов" % (host, n))'),
 ('notify.send("БАЗА слита\\n%s\\n%s" % (host, db.rsplit(":", 1)[-1]))',
  'notify.send_lvl(1, "БАЗА слита\\n%s\\n%s" % (host, db.rsplit(":", 1)[-1]))'),
 ('notify.send("ЗАКРЕПЛЕНИЕ\\n%s\\n%s" % (host, kept))',
  'notify.send_lvl(1, "ЗАКРЕПЛЕНИЕ\\n%s\\n%s" % (host, kept))'),
]
for i, (old, new) in enumerate(PAIRS, 1):
    if s.count(old) != 1:
        print("night %d: найдено %d" % (i, s.count(old))); sys.exit(1)
    s = s.replace(old, new)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("нотификации: ок")
