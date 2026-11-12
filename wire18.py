# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\panel.py"
s = io.open(P, encoding="utf-8-sig").read()
PAIRS = []

PAIRS.append((
"""def do_triage():
    while True:
        h = _next_hot()
        if not h:
            ui.clear()
            ui.banner()
            ui.head("РАЗБОР", "пусто")
            ui.say("годных целей нет")
            ui.pause()
            return
        state.acquire(h)""",
"""def do_triage():
    while True:
        h = _next_hot() or store.current()
        if not h:
            h = pick()
        if not h:
            return
        state.acquire(h)"""))

PAIRS.append((
"""            ui.item("1", "собрать досье", "всё в файл")
            ui.item("2", "инструменты", "ручные действия")
            ui.item("3", "проверить доступ", "код и размер")
            ui.item("4", "открыть сессию", "куки браузером")
            ui.item("5", "заметка", "в дневник")
            ui.item("6", "готово", "в отработанные")
            ui.item("7", "в мусор", "отсеять")
            ui.item("8", "отложить", "и следующая")
            ui.item("9", "следующая", "без отметки")
            ui.item("0", "выйти из разбора")
            c = ui.ask("пункт")
            if c == "0":
                state.release(h)
                return
            if c == "1":
                from modules import dossier
                dossier.run(h)
                ui.pause()
            elif c == "2":
                do_tools(h)
            elif c == "3":
                try:
                    r = http.get(h, "/")
                    ui.say("код %d, размер %d" % (r.status_code, len(r.content)))
                except Exception as e:
                    ui.err("сбой: %s" % e)
                ui.pause()
            elif c == "4":
                try:
                    stt = browser.grab(h, store.get(h).get("url"))
                    browser.save_state(h, stt)
                    ui.ok("кук: %d" % len(stt.get("cookies", [])))
                except Exception as e:
                    ui.err("сбой: %s" % e)
                ui.pause()
            elif c == "5":
                t = ui.ask("текст заметки")
                if t:
                    d = store.get(h)
                    d.setdefault("diary", []).append("%s %s" % (state.get(h).get("at", ""), t))
                    store.save(h, d)
                    ui.ok("записано")
                ui.pause()
            elif c == "6":
                state.set_status(h, "cracked", note="обработано")
                queue.drop_hot(h, "done")
                state.release(h)
                break
            elif c == "7":
                state.set_status(h, "trash", note="в мусор")
                queue.drop_hot(h, "trash")
                state.release(h)
                break
            elif c == "8":
                state.set_status(h, "hot", note="отложено")
                state.release(h)
                break
            elif c == "9":
                state.release(h)
                break""",
"""            ui.item("1", "собрать досье", "всё в файл")
            ui.item("2", "инструменты", "ручные действия")
            ui.item("3", "шаблоны", "библиотека дыр")
            ui.item("4", "проверить доступ", "код и размер")
            ui.item("5", "открыть сессию", "куки браузером")
            ui.item("6", "заметка", "в дневник")
            ui.item("7", "готово", "в отработанные")
            ui.item("8", "в мусор", "отсеять")
            ui.item("9", "отложить", "и следующая")
            ui.item("С", "следующая", "без отметки")
            ui.item("0", "выйти из разбора")
            c = ui.ask("пункт").upper()
            if c == "0":
                state.release(h)
                return
            if c == "1":
                do_dossier(h)
            elif c == "2":
                do_tools(h)
            elif c == "3":
                from modules import tplui
                tplui.run(h)
            elif c == "4":
                try:
                    r = http.get(h, "/")
                    ui.say("код %d, размер %d" % (r.status_code, len(r.content)))
                except Exception as e:
                    ui.err("сбой: %s" % e)
                ui.pause()
            elif c == "5":
                try:
                    stt = browser.grab(h, store.get(h).get("url"))
                    browser.save_state(h, stt)
                    ui.ok("кук: %d" % len(stt.get("cookies", [])))
                except Exception as e:
                    ui.err("сбой: %s" % e)
                ui.pause()
            elif c == "6":
                t = ui.ask("текст заметки")
                if t:
                    d = store.get(h)
                    d.setdefault("diary", []).append("%s %s" % (state.get(h).get("at", ""), t))
                    store.save(h, d)
                    ui.ok("записано")
                ui.pause()
            elif c == "7":
                state.set_status(h, "cracked", note="обработано")
                queue.drop_hot(h, "done")
                state.release(h)
                break
            elif c == "8":
                state.set_status(h, "trash", note="в мусор")
                queue.drop_hot(h, "trash")
                state.release(h)
                break
            elif c == "9":
                state.set_status(h, "hot", note="отложено")
                state.release(h)
                break
            elif c == "С":
                state.release(h)
                break"""))

PAIRS.append((
"""TOOLS = [
    ("1", "движок и версия", tool_engine, "определить CMS"),
    ("2", "профиль движка", tool_profile, "пути и поля"),
    ("3", "сторонние модули", tool_mods, "плагины, темы"),
    ("4", "поддомены", tool_subdom, "поиск по именам"),
    ("5", "архивы", tool_arch, "бэкапы наружу"),
    ("6", "админка и обходы", tool_admin, "входы, обходы"),
    ("7", "подбор пароля", tool_brute, "по словарю"),
    ("8", "повтор пароля", tool_reuse, "с других хостов"),
    ("9", "WordPress", tool_wp, "логины, плагины"),
    ("10", "слив контактов", tool_creds, "из найденных файлов"),
    ("11", "заказы OpenCart", tool_orders, "выгрузка"),
    ("12", "бэкап базы", tool_backup, "скачать дамп"),
    ("13", "закрепление", tool_keep, "свой доступ"),
    ("14", "поиск админки", tool_find_admin, "перебор путей"),
]""",
"""def tool_engine_profile(h):
    from modules import engine, profiles
    k = _kind(h)
    ui.say("движок: %s" % k)
    ui.say("версия: %s" % (engine.version(h, k) or "не определена"))
    p = profiles.get(k)
    ui.say("файлы: " + ", ".join(p.get("files", [])[:8]))
    ui.say("админка: " + ", ".join(p.get("admin", [])))
    ui.say("поле входа: " + str(p.get("login_field")))


def tool_net(h):
    from modules import arch, subdom
    got = subdom.run(h) or []
    ui.say("поддомены: " + (", ".join(got[:20]) if got else "нет"))
    ar = arch.run(h) or []
    if not ar:
        ui.say("архивы: нет")
    for u, name in ar:
        ui.say("%s  %s" % (u, name))


def tool_admin_full(h):
    tool_admin(h)
    ui.say("--- поиск админки")
    tool_find_admin(h)


def tool_data(h):
    from modules import admin, orders
    c = _creds(h)
    if not c:
        return
    ui.say("заказов: %s" % (orders.run(h, c) or "0"))
    ui.say("база: %s байт" % (admin.backup(h, c) or "0"))


TOOLS = [
    ("1", "движок и профиль", tool_engine_profile, "CMS, пути, поля"),
    ("2", "сторонние модули", tool_mods, "плагины, темы"),
    ("3", "поддомены и архивы", tool_net, "бэкапы наружу"),
    ("4", "админка и обходы", tool_admin_full, "входы, перебор путей"),
    ("5", "подбор пароля", tool_brute, "по словарю"),
    ("6", "повтор пароля", tool_reuse, "с других хостов"),
    ("7", "WordPress", tool_wp, "логины, плагины, уязвимости"),
    ("8", "слив контактов", tool_creds, "из найденных файлов"),
    ("9", "заказы и бэкап", tool_data, "выгрузка, дамп"),
    ("10", "закрепление", tool_keep, "свой доступ"),
]"""))

PAIRS.append((
"""        ui.head("СЛУЖБА", "машина " + state.machine())""",
"""        ui.head("СИСТЕМА", "машина " + state.machine())"""))

PAIRS.append((
"""def _dispatch(ch, h):
    if ch == "9":
        return False
    if ch == "1":
        do_targets()
    elif ch == "2":
        do_run()
    elif ch == "3":
        do_triage()
    elif ch in ("4", "5") and not h:
        ui.err("сначала цель")
        ui.pause()
    elif ch == "4":
        do_dossier(h)
    elif ch == "5":
        do_tools(h)
    elif ch == "6":
        do_service()
    elif ch == "7":
        from modules import tplui
        tplui.run(h)
    elif ch == "8":
        do_reports()
    return True""",
"""def _dispatch(ch, h):
    if ch == "6":
        return False
    if ch == "1":
        do_targets()
    elif ch == "2":
        do_run()
    elif ch == "3":
        do_triage()
    elif ch == "4":
        do_reports()
    elif ch == "5":
        do_service()
    return True"""))

PAIRS.append((
"""        ui.item("1", "ЦЕЛИ", "сбор, импорт, очередь, выбор")
        ui.item("2", "ПРОГОН", "массовый и ночной, STOP")
        ui.item("3", "РАЗБОР", "годное по одной")
        ui.item("4", "ДОСЬЕ", "автосбор по цели")
        ui.item("5", "ИНСТРУМЕНТЫ", "по выбранной цели")
        ui.item("6", "СЛУЖБА", "сеть, прокси, телеграм, машина")
        ui.item("7", "ШАБЛОНЫ", "библиотека дыр")
        ui.item("8", "ОТЧЁТЫ", "прогоны")
        ui.item("9", "выход")""",
"""        ui.item("1", "ЦЕЛИ", "сбор, импорт, очередь, выбор")
        ui.item("2", "ПРОГОН", "массовый и ночной, STOP")
        ui.item("3", "РАЗБОР", "досье, инструменты, шаблоны")
        ui.item("4", "ОТЧЁТЫ", "прогоны, выгрузки")
        ui.item("5", "СИСТЕМА", "сеть, прокси, телеграм, машина")
        ui.item("6", "выход")"""))

for i, (old, new) in enumerate(PAIRS, 1):
    n = s.count(old)
    if n != 1:
        print("ЗАМЕНА %d: найдено %d раз, стоп" % (i, n))
        sys.exit(1)
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("замен: %d, компиляция ок" % len(PAIRS))
