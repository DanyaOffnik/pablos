# -*- coding: utf-8 -*-
"""Проверка целостности: импорты и обязательные функции."""
import importlib
import sys

BAD = []

MODS = ["core.config", "core.http", "core.queue", "core.state", "core.store",
        "core.ui", "core.waf", "core.users", "core.findings", "core.proxies",
        "core.notify", "core.browser", "core.card", "core.checks", "core.hints",
        "core.learn", "core.stack", "core.brfetch", "core.vault", "core.verify",
        "modules.admin", "modules.adminfind", "modules.arch", "modules.brute",
        "modules.bypass", "modules.creds", "modules.dossier", "modules.engine",
        "modules.files", "modules.harvest", "modules.keep", "modules.mass",
        "modules.mods", "modules.night", "modules.nuc", "modules.orders",
        "modules.profiles", "modules.post", "modules.recon", "modules.report", "modules.reuse",
        "modules.sqli", "modules.subdom", "modules.tpl", "modules.tplui",
        "modules.wp", "modules.wpfast", "modules.wpvuln"]

for name in MODS:
    try:
        importlib.import_module(name)
        print("  ok   " + name)
    except Exception as e:
        BAD.append(name)
        print("  FAIL %s: %s: %s" % (name, type(e).__name__, str(e)[:80]))

NEED = [
    ("core.queue", ("queue", "add", "drop", "drop_hot", "restore", "trash")),
    ("core.state", ("counts", "by_status", "set_status", "acquire", "release")),
    ("core.config", ("DATA", "TPL", "PROFILES", "RUNS", "REPORTS", "DOSSIER")),
    ("modules.profiles", ("get", "PROFILES")),
    ("modules.brute", ("run", "run_batch", "_users", "PARK_FILE")),
    ("modules.tpl", ("run", "_load")),
    ("modules.report", ("run", "build")),
    ("core.waf", ("detect", "known")),
    ("core.vault", ("add", "pairs")),
    ("core.verify", ("confirm",)),
    ("modules.post", ("run",)),
]

for mod, attrs in NEED:
    try:
        m = importlib.import_module(mod)
    except Exception:
        continue
    for a in attrs:
        if not hasattr(m, a):
            BAD.append("%s.%s" % (mod, a))
            print("  FAIL нет %s.%s" % (mod, a))

print()
if BAD:
    print("ПРОБЛЕМЫ: %d" % len(BAD))
    sys.exit(1)
print("всё на месте")
