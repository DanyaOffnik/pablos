# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\harvest.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
'''    "prestashop": ['"id_product" магазин', "prestashop магазин"],
}''',
'''    "prestashop": ['"id_product" магазин', "prestashop магазин"],
    "joomla": ['"option=com_content"', '"com_content&view=article"', "joomla сайт"],
    "dle": ['"DataLife Engine"', '"engine/data/config.php"', "datalife движок"],
    "frappe": ['"api/method/ping"', "frappe crm"],
    "laravel": ['"_ignition/health-check"', "laravel сайт"],
    "django": ['"csrfmiddlewaretoken" сайт', "django сайт"],
}'''))

PAIRS.append((
'''    ("prestashop", ("prestashop", "id_product")),
)''',
'''    ("prestashop", ("prestashop", "id_product")),
    ("joomla", ("com_content", "/media/system/js/", "joomla")),
    ("dle", ("datalife", "engine/classes/")),
    ("frappe", ("/assets/frappe/", "frappe")),
    ("laravel", ("laravel", "csrf-token")),
    ("django", ("csrfmiddlewaretoken",)),
)'''))

PAIRS.append((
'''    ui.say("движки: opencart, wordpress, bitrix, prestashop")''',
'''    ui.say("движки: opencart, wordpress, bitrix, prestashop, joomla, dle, frappe, laravel, django")'''))

for i, (old, new) in enumerate(PAIRS, 1):
    if s.count(old) != 1:
        print("замена %d: найдено %d" % (i, s.count(old))); sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("движки в поиске: ок")
