# -*- coding: utf-8 -*-
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
BLINK = "\x1b[5m"
OFF = "\x1b[0m"

SKULL = [
    "              ▄▄▄▄▄▄▄▄▄▄▄▄▄",
    "           ▄█████████████████▄",
    "          █████████████████████",
    "         ████▀▀▀▀███████▀▀▀▀████",
    "         ██▀   ▄▄▄   █   ▄▄▄   ▀██",
    "         ██   █████  █  █████   ██",
    "         ██▄   ▀▀▀   █   ▀▀▀   ▄██",
    "          ████▄▄▄▄███████▄▄▄▄████",
    "           ▀███████████████████▀",
    "             ▀▀███▀▀▀▀▀███▀▀",
    "               ██       ██",
]

BANNER = [
    "  ██████╗  █████╗ ██████╗ ██╗      ██████╗ ███████╗",
    "  ██╔══██╗██╔══██╗██╔══██╗██║     ██╔═══██╗██╔════╝",
    "  ██████╔╝███████║██████╔╝██║     ██║   ██║███████╗",
    "  ██╔═══╝ ██╔══██║██╔══██╗██║     ██║   ██║╚════██║",
    "  ██║     ██║  ██║██████╔╝███████╗╚██████╔╝███████║",
    "  ╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝",
    "        ▄▀█ ▀█▀ ▀█▀ ▄▀█ █▀▀ █ █",
    "        █▀█  █   █  █▀█ █▄▄ █▄▀",
]

W = 62
SLOW = [False]

THREAT = ((8, "КРИТИЧНО", RED), (5, "ВЫСОКИЙ", DIMRED),
          (2, "СРЕДНИЙ", YELLOW), (1, "НИЗКИЙ", GREEN))


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


def _type(text, delay=0.004):
    if not SLOW[0]:
        print(text, flush=True)
        return
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print(flush=True)


def rule(ch="─"):
    print("  " + DIMRED + ch * W + OFF, flush=True)


def threat(score):
    for lim, name, color in THREAT:
        if score >= lim:
            return color, name
    return GREY, "ПУСТО"


def gauge(score, width=10):
    """Полоса угрозы от 0 до 12."""
    n = max(0, min(width, int(round(score / 12.0 * width))))
    color, _ = threat(score)
    return color + "▰" * n + GREY + "▱" * (width - n) + OFF


def banner():
    print(flush=True)
    for line in SKULL:
        print(RED + BOLD + line + OFF, flush=True)
    print(flush=True)
    for line in BANNER:
        print(RED + BOLD + line + OFF, flush=True)
    print(flush=True)
    print(DIMRED + "  ╔" + "═" * W + "╗" + OFF, flush=True)
    print(DIMRED + "  ║ " + GREY + "инструмент пробива" + OFF
          + " " * (W - 36) + GREY + "цели не свои" + OFF + DIMRED + " ║" + OFF, flush=True)
    print(DIMRED + "  ╚" + "═" * W + "╝" + OFF, flush=True)


def intro():
    """Короткая заставка при старте."""
    clear()
    for line in SKULL:
        print(RED + BOLD + line + OFF, flush=True)
        time.sleep(0.03)
    for line in BANNER:
        print(RED + BOLD + line + OFF, flush=True)
        time.sleep(0.03)
    print(flush=True)
    for t in ("инициализация ядра", "загрузка шаблонов", "проверка связи"):
        sys.stdout.write("  " + GREY + "▸ " + t + " " + OFF)
        sys.stdout.flush()
        time.sleep(0.18)
        print(GREEN + "ok" + OFF, flush=True)
    time.sleep(0.15)


def bar(t, right=""):
    t = str(t)[:W - 8]
    right = str(right)[:24]
    pad = max(0, W - len(t) - len(right) - 3)
    print(flush=True)
    print(DIMRED + "  ╔" + "═" * W + "╗" + OFF, flush=True)
    print(DIMRED + "  ║ " + RED + BOLD + "▌" + OFF + " " + WHITE + BOLD + t + OFF
          + " " * pad + YELLOW + right + OFF + " " + DIMRED + "║" + OFF, flush=True)
    print(DIMRED + "  ╚" + "═" * W + "╝" + OFF, flush=True)


def head(t, right=""):
    bar(t, right)


def say(m=""):
    print("  " + str(m), flush=True)


def kv(k, v, color=WHITE):
    print("  " + GREY + str(k).ljust(18) + OFF + color + str(v) + OFF, flush=True)


def ok(m):
    print("  " + GREEN + "▸ [" + "+" + "] " + str(m) + OFF, flush=True)


def warn(m):
    print("  " + YELLOW + "▸ [!] " + str(m) + OFF, flush=True)


def err(m):
    print("  " + RED + "▸ [" + "x" + "] " + str(m) + OFF, flush=True)


def alert(m):
    print(flush=True)
    print(RED + BOLD + "  ╔" + "═" * W + "╗" + OFF, flush=True)
    print(RED + BOLD + "  ║ " + str(m)[:W - 4].ljust(W - 2) + "║" + OFF, flush=True)
    print(RED + BOLD + "  ╚" + "═" * W + "╝" + OFF, flush=True)
    print(flush=True)


def item(n, text, hint=""):
    num = RED + BOLD + "[" + str(n).rjust(2) + "]" + OFF
    tail = ("   " + GREY + hint + OFF) if hint else ""
    print("  " + num + " " + WHITE + str(text) + OFF + tail, flush=True)


def row(score, host, notes):
    color, name = threat(score)
    print("  " + gauge(score) + " " + color + ("%3d" % score) + OFF + "  "
          + WHITE + ("%-30s" % host) + OFF + " " + GREY + str(notes)[:34] + OFF, flush=True)


def ask(p, d=""):
    tail = (" [" + str(d) + "]") if d else ""
    v = input("  " + DIMRED + "┌─" + OFF + CYAN + BOLD + " " + str(p) + tail + OFF
              + DIMRED + " ▸ " + OFF).strip()
    return v or d


def pause():
    input("  " + GREY + "─ Enter ─" + OFF)
