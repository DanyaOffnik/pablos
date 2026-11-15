import os
import threading
import time

from core import vuln


def _ui():
    from panel import ui
    return ui


def _stop():
    from panel import STOP
    return os.path.isfile(STOP)


S = {"cve": None, "threads": 10, "tmo": 30}
JOB = {"t": None}


def _paint(ui):
    rows = vuln.tail(S["cve"], 25)
    ui.clear()
    ui.banner()
    ui.head("VULN", S["cve"] or "-")
    c = {"owned": 0, "confirmed": 0, "not_vuln": 0, "error": 0, "prefilter_fail": 0}
    for r in vuln.tail(S["cve"], 10000):
        c[r.get("state")] = c.get(r.get("state"), 0) + 1
    for r in rows:
        ui.say("%-34s %-7s %-12s %s" % (r.get("host", "")[:34], r.get("version", "-"),
                                        r.get("state", ""), r.get("evidence", "")[:40]))
    ui.say("")
    ui.say("проверено %d | взято %d | подтверждено %d | мимо %d | ошибок %d"
           % (sum(c.values()), c["owned"], c["confirmed"], c["not_vuln"], c["error"]))
    if JOB["t"] and JOB["t"].is_alive():
        ui.say("РАБОТАЕТ")


def _watch():
    ui = _ui()
    while JOB["t"] and JOB["t"].is_alive():
        _paint(ui)
        time.sleep(2)
    _paint(ui)
    ui.pause()


def _pick(ui):
    while True:
        ui.clear()
        ui.banner()
        ui.head("VULN", "выбор уязвимости")
        cat = vuln.catalog()
        for i, (cid, title, plug) in enumerate(cat, 1):
            ui.item(str(i), plug, title[:50])
        ui.item("0", "назад")
        c = ui.ask("номер")
        if c == "0":
            return False
        if c.isdigit() and 1 <= int(c) <= len(cat):
            S["cve"] = cat[int(c) - 1][0]
            return True


def _paste(ui):
    ui.clear()
    ui.head("ВСТАВКА", "по одному, пусто — конец")
    got = []
    while True:
        h = ui.ask("домен")
        if not h:
            break
        got.append(h)
    if got:
        vuln.append_list(S["cve"], got)
    ui.ok("добавлено: %d" % len(got))
    ui.pause()


def _footprint(ui):
    v = vuln.load(S["cve"])
    fp = v.get("footprint") or []
    if not fp:
        first = (v.get("oracles") or [{}])[0].get("path", "")
        slug = v.get("plugin", "")
        fp = ['publicwww: "%s"' % first,
              'shodan:    http.html:"%s"' % slug,
              'google:    inurl:"%s"' % first]
    ui.clear()
    ui.head("ГДЕ ИСКАТЬ", v.get("plugin", ""))
    for line in fp:
        ui.say(line)
    ui.say("")
    ui.pause()


def _start(ui):
    if JOB["t"] and JOB["t"].is_alive():
        ui.say("уже работает")
        ui.pause()
        return
    hosts = vuln.sources_file(vuln.list_path(S["cve"])) if os.path.isfile(vuln.list_path(S["cve"])) else []
    if not hosts:
        ui.say("список пуст")
        ui.pause()
        return
    JOB["t"] = threading.Thread(target=vuln.run, args=(S["cve"], hosts, S["threads"], S["tmo"]),
                                kwargs={"stop_fn": _stop}, daemon=True)
    JOB["t"].start()
    _watch()


def _grab(ui):
    rows = vuln.grab(S["cve"])
    if not rows:
        ui.say("нечего забирать")
        ui.pause()
        return
    p = os.path.join(vuln.DB, S["cve"], "owned.txt")
    with open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(r["host"] + "\t" + r.get("shell", "") + "\n")
    ui.ok("взято %d -> %s" % (len(rows), p))
    ui.pause()


def _tonight(ui):
    rows = vuln.grab(S["cve"])
    if not rows:
        ui.say("нечего отправлять")
        ui.pause()
        return
    from panel import queue, state
    for r in rows:
        queue.restore(r["host"])
        state.set_status(r["host"].lower(), "new")
    ui.ok("в ночную очередь: %d" % len(rows))
    ui.pause()


def run():
    ui = _ui()
    if not S["cve"] and not _pick(ui):
        return
    while True:
        _paint(ui)
        ui.say("")
        ui.item("ENTER", "старт", "")
        ui.item("v", "вставить домены", "")
        ui.item("f", "где искать", "")
        ui.item("g", "забрать взятое", "")
        ui.item("n", "в ночную очередь", "")
        ui.item("t", "потоки / таймаут", "")
        ui.item("c", "сменить CVE", "")
        ui.item("0", "назад")
        c = ui.ask("пункт").lower()
        if c == "0":
            return
        if c == "":
            _start(ui)
        elif c == "v":
            _paste(ui)
        elif c == "f":
            _footprint(ui)
        elif c == "g":
            _grab(ui)
        elif c == "n":
            _tonight(ui)
        elif c == "t":
            S["threads"] = int(ui.ask("потоков") or S["threads"])
            S["tmo"] = int(ui.ask("таймаут") or S["tmo"])
        elif c == "c":
            _pick(ui)