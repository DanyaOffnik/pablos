# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\modules\profiles.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """    "django": {"""
new = """    "joomla": {
        "files": ["/configuration.php", "/configuration.php~", "/configuration.php.bak",
                  "/administrator/manifests/files/joomla.xml", "/administrator/",
                  "/.env", "/.git/config", "/backup.sql", "/dump.sql"],
        "admin": ["/administrator/", "/administrator/index.php"],
        "params": [("/", "searchword", "a"),
                   ("/index.php?option=com_content&view=article", "id", "1")],
        "login_field": "username",
    },
    "dle": {
        "files": ["/engine/data/config.php", "/engine/data/dbconfig.php",
                  "/admin.php", "/backup/", "/.env", "/.git/config"],
        "admin": ["/admin.php"],
        "params": [("/index.php?do=search&subaction=search", "story", "a"),
                   ("/", "do", "search")],
        "login_field": "login_name",
    },
    "django": {"""
if s.count(old) != 1:
    print("profiles: не найдено"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)

P = r"C:\work\hunt2\modules\engine.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """    ("laravel", ("laravel", "csrf-token")),"""
new = """    ("joomla", ("/media/system/js/", "com_content", "/components/com_", "joomla")),
    ("dle", ("datalife", "engine/classes/", "engine/ajax/")),
    ("laravel", ("laravel", "csrf-token")),"""
if s.count(old) != 1:
    print("engine: MARKS не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """    "prestashop": [re.compile(r"PrestaShop\\s*([0-9.]+)", re.I)],"""
new2 = """    "prestashop": [re.compile(r"PrestaShop\\s*([0-9.]+)", re.I)],
    "joomla": [re.compile(r'content="Joomla!\\s*([0-9.]+)', re.I),
               re.compile(r"<version>([0-9.]+)</version>")],
    "dle": [re.compile(r"DataLife Engine[^0-9]{0,20}([0-9.]+)", re.I)],"""
if s.count(old2) != 1:
    print("engine: VER не найдено"); sys.exit(1)
s = s.replace(old2, new2)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("профили и детект: ок")
