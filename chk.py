import glob
p = "panel.py"
t = open(p, encoding="utf-8-sig").read()
print("в panel.py есть 'поиск по дырам':", "поиск по дырам" in t)
print("в panel.py есть 'vulntab':", "vulntab" in t)
print("do_run в panel.py:", t.count("def do_run"))
for f in glob.glob("**/*.py", recursive=True):
    try:
        x = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    if "возобновить отложенные" in x:
        print("меню с пунктом 5 лежит в:", f, "| def do_run:", x.count("def do_run"))