import io, os, shutil
p = r"C:\work\hunt2\modules\night.py"
shutil.copy(p, p + ".bak")
s = io.open(p, encoding="utf-8-sig").read()
orig = s

def cut(s, a, b, new):
    i = s.index(a); j = s.index(b, i)
    return s[:i] + new + s[j:]

s = s.replace("SEM = threading.Semaphore(2)\n",
              "SEM = threading.Semaphore(2)\nSLOTS = threading.BoundedSemaphore(16)\n", 1)

s = s.replace("def _work(host, st, use_browser, full):\n    rec = st.get(host) or {}\n",
              "def _work(host, st, use_browser, full):\n    rec = st.get(host) or {}\n"
              "    _TL.deadline = time.time() + 600\n", 1)

NEW_CALL = '''def _call(fn, limit, *a):
    buf = sio.StringIO()
    box = {}
    dl = getattr(_TL, "deadline", 0)
    if dl:
        left = dl - time.time()
        if left <= 3:
            return "", None, "\u0431\u044e\u0434\u0436\u0435\u0442"
        limit = min(limit or STAGE_LIMIT, left)
    if not SLOTS.acquire(timeout=5):
        return "", None, "\u043e\u0447\u0435\u0440\u0435\u0434\u044c"

    def _t():
        _TL.buf = buf
        try:
            box["out"] = fn(*a)
        except BaseException as e:
            box["err"] = e
        finally:
            _TL.buf = None

    th = threading.Thread(target=_t, daemon=True)
    th.start()
    th.join(limit or STAGE_LIMIT)
    alive = th.is_alive()
    SLOTS.release()
    if alive:
        return buf.getvalue(), None, "\u0442\u0430\u0439\u043c\u0430\u0443\u0442"
    if "err" in box:
        return buf.getvalue(), None, str(box["err"]).splitlines()[0]
    return buf.getvalue(), box.get("out"), ""


'''

NEW_DRAW = '''_PAINT = [False]


def _draw(st, done, total, order, workers=0):
    w = sys.stdout
    w.write("\\033[H")
    ui.banner()
    ui.head("\u041d\u041e\u0427\u041d\u041e\u0419 \u041f\u0420\u041e\u0413\u041e\u041d",
            "%d / %d  \u043f\u043e\u0442\u043e\u043a\u043e\u0432 %d" % (done, total, workers))
    live = [h for h in order if not (st.get(h) or {}).get("done")]
    fin = [h for h in order if (st.get(h) or {}).get("done")]
    show = live[:26] + fin[-4:]
    for host in show:
        _row(host, st.get(host) or {})
    if len(order) > len(show):
        print("  ... \u0435\u0449\u0451 %d" % (len(order) - len(show)))
    if TAIL:
        print()
        for line in TAIL[-4:]:
            print("  " + ui.YELLOW + "  ! " + line + ui.OFF)
    if os.path.isfile(STOP):
        print()
        ui.warn("\u043d\u0430\u0439\u0434\u0435\u043d STOP, \u0432\u0441\u0442\u0430\u044e \u043f\u043e\u0441\u043b\u0435 \u0442\u0435\u043a\u0443\u0449\u0438\u0445")
    w.write("\\033[J")
    try:
        w.flush()
    except Exception:
        pass


def _painter(st, box, total, stop, order, workers=0):
    while not stop.wait(1.5):
        if _PAINT[0]:
            continue
        _PAINT[0] = True
        try:
            _draw(st, box[0], total, order, workers)
        except Exception:
            pass
        finally:
            _PAINT[0] = False


'''

s = cut(s, "def _call(fn, limit, *a):", "def _blocked(host):", NEW_CALL)
s = cut(s, "def _draw(st, done, total, order, workers=0):", "def run(only=None", NEW_DRAW)

if s == orig:
    print("НЕ ИЗМЕНЕНО — маркеры не найдены")
else:
    io.open(p, "w", encoding="utf-8-sig", newline="\n").write(s)
    print("патч накатан, бэкап:", p + ".bak")
