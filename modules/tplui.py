# -*- coding: utf-8 -*-
import io
import json
import os
import subprocess

from core import config, ui
from modules import tpl

TPL = config.TPL


def _files():
    if not os.path.isdir(TPL):
        return []
    return sorted(n for n in os.listdir(TPL) if n.endswith(".json") or n.endswith(".json.off"))


def _read(name):
    try:
        with open(os.path.join(TPL, name), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _toggle(name):
    p = os.path.join(TPL, name)
    if name.endswith(".off"):
        os.replace(p, p[:-4])
        return name[:-4]
    os.replace(p, p + ".off")
    return name + ".off"


def _edit(name):
    p = os.path.join(TPL, name)
    try:
        subprocess.Popen(["notepad.exe", p])
        ui.say("открыл в блокноте: " + p)
    except Exception as e:
        ui.err("не открылось: %s" % e)


def _add():
    tid = ui.ask("id (латиницей, без пробелов)")
    if not tid:
        return
    eng = ui.ask("движок (opencart/wordpress/prestashop/bitrix/*)", "opencart")
    path = ui.ask("путь (можно {{p}} вместо значения)")
    if not path:
        return
    where = ui.ask("куда значение: query / post-form / post-json", "query")
    param = ""
    body_tpl = ""
    if where == "query":
        param = ui.ask("имя параметра")
    elif where == "post-form":
        param = ui.ask("имя поля")
    else:
        body_tpl = ui.ask("тело с {{p}}")
    mt = ui.ask("признак: time / body / regex / status / diff", "time")
    val = ""
    if mt in ("time", "body", "regex", "status"):
        val = ui.ask("значение признака")
    payloads = [x.strip() for x in ui.ask("нагрузки через |").split("|") if x.strip()]
    if not payloads:
        return
    t = {"id": tid, "engine": eng, "path": path, "payloads": payloads,
         "match": {"type": mt}, "score": 6}
    if param:
        t["param"] = param
    if body_tpl:
        t["body_tpl"] = body_tpl
    if val:
        t["match"]["value"] = val if mt != "time" else float(val)
    req = ui.ask("условие применимости (подстрока в ответе, пусто = нет)")
    if req:
        t["require"] = req
    with open(os.path.join(TPL, tid + ".json"), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=2)
    ui.ok("добавлен: " + tid)


def run(h):
    while True:
        ui.clear()
        ui.banner()
        files = _files()
        on = len([f for f in files if not f.endswith(".off")])
        ui.head("ШАБЛОНЫ ДЫР", "включено %d из %d" % (on, len(files)))
        for i, n in enumerate(files, 1):
            t = _read(n)
            mark = " " if not n.endswith(".off") else "-"
            ui.say("%s %2d. %-34s %-12s %s" % (mark, i, n.replace(".json.off", "").replace(".json", ""),
                                               t.get("engine", "?"), (t.get("match") or {}).get("type", "?")))
        print()
        ui.item("1", "включить или выключить", "номер строки")
        ui.item("2", "править в блокноте", "номер строки")
        ui.item("3", "добавить", "новый шаблон")
        ui.item("4", "прогнать по цели", "только текущая")
        ui.item("0", "назад")
        c = ui.ask("пункт")
        if c == "0":
            return
        if c == "1":
            n = ui.ask("номер или имя файла")
            if n.isdigit() and 1 <= int(n) <= len(files):
                n = files[int(n) - 1]
            if n in files:
                ui.ok("стало: " + _toggle(n))
            ui.pause()
        elif c == "2":
            n = ui.ask("номер или имя файла")
            if n.isdigit() and 1 <= int(n) <= len(files):
                n = files[int(n) - 1]
            if n in files:
                _edit(n)
            ui.pause()
        elif c == "3":
            _add()
            ui.pause()
        elif c == "4":
            if not h:
                ui.err("сначала цель")
                ui.pause()
                continue
            from modules import engine as eng_mod
            try:
                k = eng_mod.detect(h)
                if isinstance(k, tuple):
                    k = k[0]
            except Exception:
                k = ""
            got = tpl.run(h, k or "")
            for f in got:
                ui.ok("%s [%s]" % (f["tag"], f["url"]))
            ui.pause()
