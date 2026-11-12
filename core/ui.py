# -*- coding: utf-8 -*-
import sys

RED = "\x1b[91m"
DIMRED = "\x1b[31m"
CYAN = "\x1b[96m"
GREY = "\x1b[90m"
WHITE = "\x1b[97m"
YELLOW = "\x1b[93m"
GREEN = "\x1b[92m"
BOLD = "\x1b[1m"
OFF = "\x1b[0m"

BANNER = [
    "  ██████╗  █████╗ ██████╗ ██╗      ██████╗ ███████╗",
    "  ██╔══██╗██╔══██╗██╔══██╗██║     ██╔═══██╗██╔════╝",
    "  ██████╔╝███████║██████╔╝██║     ██║   ██║███████╗",
    "  ██╔═══╝ ██╔══██║██╔══██╗██║     ██║   ██║╚════██║",
    "  ██║     ██║  ██║██████╔╝███████╗╚██████╔╝███████║",
    "  ╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝",
    "            ▄▀█ ▀█▀ ▀█▀ ▄▀█ █▀▀ █ █",
    "            █▀█  █   █  █▀█ █▄▄ █▄▀",
]

W = 58


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


def row(score, host, notes):
    if score >= 7:
        c = RED
    elif score >= 4:
        c = YELLOW
    elif score > 0:
        c = GREEN
    else:
        c = GREY
    print("  " + c + "%-30s %3d  %s" % (host, score, notes) + OFF, flush=True)


def banner():
    print()
    for line in BANNER:
        print(RED + BOLD + line + OFF, flush=True)
    print()
    print(GREY + "  " + "-" * W + OFF, flush=True)
    print(GREY + "  инструмент пробива · версия 1.0 · только свои цели" + OFF, flush=True)
    print(GREY + "  " + "-" * W + OFF, flush=True)


def bar(t, right=""):
    line = "  " + t
    pad = max(0, W - len(t) - len(right) - 2)
    print()
    print(RED + "  ┌" + "─" * W + "┐" + OFF, flush=True)
    print(RED + "  │ " + WHITE + BOLD + t + OFF + " " * pad + GREY + right + " " + RED + "│" + OFF, flush=True)
    print(RED + "  └" + "─" * W + "┘" + OFF, flush=True)


def head(t, right=""):
    bar(t, right)


def say(m=""):
    print("  " + str(m), flush=True)


def ok(m):
    print("  " + GREEN + "+ " + str(m) + OFF, flush=True)


def warn(m):
    print("  " + YELLOW + "! " + str(m) + OFF, flush=True)


def err(m):
    print("  " + RED + "x " + str(m) + OFF, flush=True)


def item(n, text, hint=""):
    tail = ("  " + GREY + hint + OFF) if hint else ""
    print("  " + RED + "[" + n + "]" + OFF + " " + WHITE + text + OFF + tail, flush=True)


def ask(p, d=""):
    tail = (" [" + d + "]") if d else ""
    v = input("  " + CYAN + p + tail + ":" + OFF + " ").strip()
    return v or d


def pause():
    input("  " + GREY + "Enter - назад" + OFF)
