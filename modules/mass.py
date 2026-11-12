# -*- coding: utf-8 -*-
import csv
import hashlib
import os
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from core import checks, config, http, queue, state, ui

CHECKS = [
    ("/system/storage/logs/error.log", 5, "лог"),
    ("/storage/logs/error.log", 4, "лог2"),
    ("/config.php", 3, "config"),
    ("/.env", 3, "env"),
    ("/adminer.php", 3, "adminer"),
    ("/config-dist.php", 2, "config-dist"),
    ("/admin/", 2, "админка"),
    ("/install/", 2, "install"),
    ("/phpmyadmin/", 2, "pma"),
    ("/.git/HEAD", 2, "git"),
    ("/pma/", 1, "pma2"),
    ("/server-status", 1, "status"),
]

ENGINES = (
    ("wordpress", ("wp-content", "wp-includes", "wp-json")),
    ("opencart", ("route=product", "catalog/view", "oc_", "index.php?route=")),
    ("bitrix", ("bitrix", "bx-")),
    ("prestashop", ("prestashop", "id_product", "modules/ps_")),
    ("laravel", ("laravel", "xsrf-token")),
    ("django", ("csrfmiddlewaretoken", "django")),
)

STOP = os.path.join(config.DATA, "STOP")
DRAW_EVERY = 0.3
FAST = 6
SLOW = 10
HASHES = {}


def _title(body):
    low = body.lower()
    if "<title>" not in low:
        return ""
    a = low.index("<title>") + 7
    b = low.find("</title>", a)
    if b < 0:
        return ""
    return body[a:b].strip()[:60]


def _engine(body, headers):
    blob = (body[:60000] + " " + str(headers)).lower()
    for name, keys in ENGINES:
        for k in keys:
            if k in blob:
                return name
    return ""


def _get(host, path, timeout):
    try:
        return http.get(host, path, timeout=timeout)
    except Exception:
        return None


def scan(host):
    r = _get(host, "/", FAST)
    if r is None:
        r = _get(host, "/", FAST)
    if r is None:
        return host, -2, "нет связи", ""

    low = r.text[:3000].lower()
    if r.status_code in (403, 503) or "just a moment" in low:
        return host, -1, "защита", ""
    if r.status_code != 200:
        return host, -1, "главная %d" % r.status_code, ""
    if len(r.content) < 1500:
        return host, 0, "заглушка", _title(r.text)

    body = r.text
    home_title = _title(body)
    home_len = len(r.content)
    kind = _engine(body, r.headers)

    h = hashlib.sha1(body.encode("utf-8", "ignore")).hexdigest()
    if kind not in ("wordpress", "opencart", "bitrix", "prestashop", "laravel", "django"):
        if h in HASHES:
            return host, 0, "дубль", home_title
        if len(HASHES) < 200000:
            HASHES[h] = host

    nf = _get(host, "/zz_none_%d.html" % int(time.time()), SLOW)
    nf_title = _title(nf.text) if nf is not None else ""
    nf_len = len(nf.content) if nf is not None else 0

    score = 2 if kind else 0
    notes = [kind] if kind else []

    for path, weight, name in CHECKS:
        x = _get(host, path, SLOW)
        if x is None:
            continue
        t = _title(x.text)
        ln = len(x.content)
        if t and (abs(ln - home_len) < max(2500, home_len // 20)
                  or abs(ln - nf_len) < max(2500, nf_len // 20)) and t in (home_title, nf_title):
            continue
        if path == "/server-status":
            if x.status_code == 401:
                score += weight
                notes.append(name)
            continue
        if x.status_code == 200 and len(x.content) > 20:
            if checks.real(path, x.text):
                score += weight
                notes.append(name)
        elif x.status_code == 403 and path in ("/.env", "/.git/HEAD"):
            score += 1
            notes.append(name + "?")
    return host, score, ", ".join(notes), home_title


def _draw(rows, done, total, phase):
    ui.clear()
    ui.banner()
    ui.head("МАССОВЫЙ ПРОГОН · " + phase, "%d / %d" % (done, total))
    for host, score, notes, title in sorted(rows, key=lambda x: -x[1])[:18]:
        ui.row(score, host, notes)


def run():
    hosts = queue.queue()
    if not hosts:
        ui.say("список пуст")
        return

    total = len(hosts)
    ui.say("целей: %d" % total)
    workers = ui.ask("потоков", "24")
    try:
        workers = max(1, min(48, int(workers)))
    except Exception:
        workers = 24

    rows = []
    done = 0
    last = [0.0]
    stop = [False]
    _draw(rows, done, total, "предфильтр")

    window = max(4, workers * 2)
    pending = set()
    it = iter(hosts)
    pool = ThreadPoolExecutor(max_workers=workers)

    def fill():
        while len(pending) < window and not stop[0]:
            try:
                h = next(it)
            except StopIteration:
                return
            pending.add(pool.submit(scan, h))

    try:
        fill()
        while pending:
            fin, pending = wait(pending, return_when=FIRST_COMPLETED)
            for fut in fin:
                try:
                    rows.append(fut.result())
                except Exception as e:
                    rows.append(("?", -3, "сбой: " + type(e).__name__, ""))
                done += 1
            now = time.time()
            if now - last[0] >= DRAW_EVERY:
                last[0] = now
                _draw(rows, done, total, "скан")
            if os.path.isfile(STOP):
                stop[0] = True
                break
            fill()
    finally:
        pool.shutdown(wait=False)

    out = os.path.join(config.REPORTS, "mass_%s.csv" % time.strftime("%Y%m%d_%H%M%S"))
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["хост", "баллы", "находки", "заголовок"])
        w.writerows(rows)

    ui.clear()
    ui.banner()
    ui.head("ИТОГ ПРОГОНА", "%d из %d" % (done, total))
    top = [r for r in sorted(rows, key=lambda x: -x[1]) if r[1] > 0]
    if top:
        for host, score, notes, _ in top[:20]:
            ui.row(score, host, notes)
    else:
        ui.say("пусто")
    print()
    if stop[0]:
        ui.warn("остановлено по STOP")
    ui.say("отчёт: " + out)

    good = [r[0] for r in rows if r[1] > 0]
    junk = [r[0] for r in rows if r[1] <= 0 and r[0] != "?"]
    ui.say("годных: %d, мусора: %d" % (len(good), len(junk)))
    if ui.ask("разложить списки (1 да / 0 нет)", "1") == "1":
        for h in good:
            state.set_status(h, "hot", note="после массового")
            queue.add_hot(h)
            queue.drop(h, "done")
        for h in junk:
            state.set_status(h, "trash", note="пусто")
            queue.drop(h, "trash")
        ui.ok("годное в разбор, мусор в мусор")
