# -*- coding: utf-8 -*-
"""Терминальный вывод. Ширина фиксированная, рамки считаются точно."""
import shutil
import sys
import time

RED = "\x1b[91m"
DIMRED = "\x1b[31m"
CYAN = "\x1b[96m"
GREY = "\x1b[90m"
WHITE = "\x1b[97m"
YELLOW = "\x1b[93m"
GREEN = "\x1b[92m"
BOLD = "\x1b[1m"
OFF = "\x1b[0m"

def _w():
    try:
        return max(46, min(70, shutil.get_terminal_size().columns - 6))
    except Exception:
        return 60

W = _w()
SLOW = [False]


def enable():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-11)
        m = ctypes.c_uint32()
        k.GetConsoleMode(h, ctypes.byref(m))
        k.SetConsoleMode(h, m.value | 0x0004)
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass


def clear():
    sys.stdout.write("\x1b[H\x1b[2J\x1b[3J")
    sys.stdout.flush()


def _line(left, right, color=RED, left_color=WHITE, right_color=GREY):
    """Строка рамки ровно по ширине W."""
    r = str(right)[:24]
    l = str(left)
    pad = W - len(l) - len(r)
    if pad < 0:
        l = l[:max(0, W - len(r))]
        pad = 0
    print("  " + color + "│" + OFF + left_color + l + " " * pad
          + right_color + r + OFF + color + "│" + OFF, flush=True)


def banner():
    print(flush=True)
    print("  " + RED + "┌" + "─" * W + "┐" + OFF, flush=True)
    _line("  P A B L O S", "v1.0")
    print("  " + RED + "├" + "─" * W + "┤" + OFF, flush=True)
    _line("  инструмент пробива", "цели не свои", GREY, GREY, GREY)
    print("  " + RED + "└" + "─" * W + "┘" + OFF, flush=True)


def intro():
    clear()
    banner()
    print(flush=True)
    for t in ("ядро", "шаблоны", "связь"):
        sys.stdout.write("  " + GREY + "  " + t.ljust(12) + OFF)
        sys.stdout.flush()
        time.sleep(0.15)
        print(GREEN + "ok" + OFF, flush=True)


def bar(t, right=""):
    print(flush=True)
    print("  " + DIMRED + "┌" + "─" * W + "┐" + OFF, flush=True)
    _line("  " + str(t).upper(), right, DIMRED, WHITE + BOLD, GREY)
    print("  " + DIMRED + "└" + "─" * W + "┘" + OFF, flush=True)


def head(t, right=""):
    bar(t, right)


def rule():
    print("  " + GREY + "  " + "─" * (W - 2) + OFF, flush=True)


def say(m=""):
    print("  " + str(m), flush=True)


def kv(k, v, color=WHITE):
    print("  " + GREY + "  " + str(k).ljust(20) + OFF + color + str(v) + OFF, flush=True)


def ok(m):
    print("  " + GREEN + "  OK   " + OFF + str(m), flush=True)


def warn(m):
    print("  " + YELLOW + "  WARN " + OFF + str(m), flush=True)


def err(m):
    print("  " + RED + "  ERR  " + OFF + str(m), flush=True)


def alert(m):
    print(flush=True)
    print("  " + RED + BOLD + "┌" + "─" * W + "┐" + OFF, flush=True)
    _line("  " + str(m), "", RED, RED + BOLD, RED)
    print("  " + RED + BOLD + "└" + "─" * W + "┘" + OFF, flush=True)
    print(flush=True)


def item(n, text, hint=""):
    tail = ("   " + GREY + hint + OFF) if hint else ""
    print("  " + RED + "%2s" % str(n) + OFF + "  " + WHITE + str(text) + OFF + tail, flush=True)


def threat(score):
    if score >= 7:
        return RED
    if score >= 4:
        return YELLOW
    if score > 0:
        return GREEN
    return GREY


def row(score, host, notes):
    c = threat(score)
    print("  " + c + "%3d" % score + OFF + "  " + WHITE + ("%-34s" % str(host))[:34] + OFF
          + " " + GREY + str(notes)[:30] + OFF, flush=True)


def ask(p, d=""):
    tail = (" [" + str(d) + "]") if d else ""
    v = input("  " + CYAN + "> " + str(p) + tail + ":" + OFF + " ").strip()
    return v or d


def pause():
    input("  " + GREY + "  Enter" + OFF)
