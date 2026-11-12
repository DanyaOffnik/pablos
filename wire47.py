# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\core\ui.py"
s = io.open(P, encoding="utf-8-sig").read()
old = """def ask(p, d=""):
    tail = (" [" + str(d) + "]") if d else ""
    v = input("  " + CYAN + "> " + str(p) + tail + ":" + OFF + " ").strip()
    return v or d


def pause():
    input("  " + GREY + "  Enter" + OFF)"""
new = """def ask(p, d=""):
    tail = (" [" + str(d) + "]") if d else ""
    try:
        v = input("  " + CYAN + "> " + str(p) + tail + ":" + OFF + " ").strip()
    except (EOFError, KeyboardInterrupt):
        return d
    return v or d


def pause():
    try:
        input("  " + GREY + "  Enter" + OFF)
    except (EOFError, KeyboardInterrupt):
        pass"""
if s.count(old) != 1:
    print("ui: не найдено"); sys.exit(1)
io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s.replace(old, new))
py_compile.compile(P, doraise=True)

P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """def _log(msg):
    with LOCK:
        try:"""
new = """TAIL = []


def _log(msg):
    with LOCK:
        TAIL.append("%s %s" % (time.strftime("%H:%M:%S"), str(msg)[:90]))
        del TAIL[:-6]
        try:"""
if s.count(old) != 1:
    print("night: _log не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """    for host in order:
        _row(host, st.get(host) or {})
    if os.path.isfile(STOP):"""
new2 = """    for host in order:
        _row(host, st.get(host) or {})
    if TAIL:
        print()
        for line in TAIL:
            print("  " + ui.YELLOW + "  ! " + line + ui.OFF)
    if os.path.isfile(STOP):"""
if s.count(old2) != 1:
    print("night: _draw не найдено"); sys.exit(1)
s = s.replace(old2, new2)

old3 = """        while pending:
            fin, pending = wait(pending, return_when=FIRST_COMPLETED)"""
new3 = """        while pending:
            try:
                fin, pending = wait(pending, return_when=FIRST_COMPLETED)
            except KeyboardInterrupt:
                ui.warn("прервано с клавиатуры, дочищаю")
                break"""
if s.count(old3) != 1:
    print("night: цикл не найден"); sys.exit(1)
s = s.replace(old3, new3)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
