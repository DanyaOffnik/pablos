# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

# 1. обрезка ошибок и полная трассировка (wire51 не применился)
PAIRS.append((
"""        TAIL.append("%s %s" % (time.strftime("%H:%M:%S"), str(msg)[:90]))""",
"""        TAIL.append("%s %s" % (time.strftime("%H:%M:%S"), str(msg)[:300]))"""))

PAIRS.append((
"""                except Exception as e:
                    _log("цель: " + traceback.format_exc(limit=1).replace("\\n", " "))""",
"""                except Exception:
                    _log("цель: " + traceback.format_exc().replace("\\n", " | ")[:400])"""))

# 2. joomla, dle, frappe выкидывались в мусор
PAIRS.append((
"""    if kind not in ("opencart", "wordpress", "bitrix", "prestashop", "laravel", "django"):""",
"""    if kind not in ("opencart", "wordpress", "bitrix", "prestashop", "laravel",
                    "django", "joomla", "dle", "frappe"):"""))

# 3. STAGE на 8 потоков: несколько зависаний блокировали все вызовы
PAIRS.append((
"""STAGE = ThreadPoolExecutor(max_workers=8)""",
"""STAGE = ThreadPoolExecutor(max_workers=16)"""))

# 4. hits[0][0] ломался, если adminfind вернул строки
PAIRS.append((
"""            if hits:
                rec["notes"].append("админка: " + hits[0][0])
                has_admin = True""",
"""            if hits:
                first = hits[0]
                rec["notes"].append("админка: " + (first[0] if isinstance(first, (list, tuple)) else str(first)))
                has_admin = True"""))

PAIRS.append((
"""            login = hits[0][0] if hits else \"\"""",
"""            login = (hits[0][0] if isinstance(hits[0], (list, tuple)) else str(hits[0])) if hits else \"\""""))

# 5. забытый STOP тормозил новый прогон сразу после старта
PAIRS.append((
"""    os.makedirs(RUN, exist_ok=True)
    st = _load()""",
"""    os.makedirs(RUN, exist_ok=True)
    if os.path.isfile(STOP):
        ui.warn("найден старый STOP — сними его, иначе прогон встанет сразу")
    st = _load()"""))

for i, (old, new) in enumerate(PAIRS, 1):
    if s.count(old) != 1:
        print("замена %d: найдено %d" % (i, s.count(old))); sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("исправлено: %d" % len(PAIRS))
