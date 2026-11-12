# -*- coding: utf-8 -*-
import os
import sys
import time

from core import config, http, state, ui
from modules import arch, bypass, engine, files, mass, mods, profiles, subdom

DOSSIER = config.DOSSIER


def _sec(title):
    return "\n=== %s ===\n" % title


def _hdr(r):
    keep = ("server", "x-powered-by", "content-type", "location", "set-cookie",
            "x-frame-options", "strict-transport-security")
    out = []
    for k in keep:
        v = r.headers.get(k)
        if v:
            out.append("%s: %s" % (k, v[:120]))
    return "\n".join(out)


def build(host):
    os.makedirs(DOSSIER, exist_ok=True)
    parts = ["ДОСЬЕ %s\nсобрано %s\nмашина %s" % (host, time.strftime("%Y-%m-%d %H:%M"), state.machine())]

    kind = "неизвестно"
    try:
        k = engine.detect(host)
        if isinstance(k, tuple):
            k = k[0]
        kind = k or "неизвестно"
    except Exception as e:
        parts.append(_sec("движок") + "сбой: %s" % e)
    parts.append(_sec("движок") + kind)

    try:
        v = engine.version(host, kind) or ""
        parts.append(_sec("версия") + (str(v) or "не определена"))
    except Exception:
        parts.append(_sec("версия") + "не определена")

    try:
        r = http.get(host, "/", timeout=20)
        parts.append(_sec("главная"))
        parts.append("код %d, размер %d, финальный адрес %s" % (r.status_code, len(r.content), r.url))
        parts.append("заголовок: " + mass._title(r.text))
        parts.append(_hdr(r))
    except Exception as e:
        parts.append(_sec("главная") + "сбой: %s" % e)

    prof = profiles.get(kind)
    parts.append(_sec("профиль путей"))
    parts.append("файлы: " + ", ".join(prof.get("files", [])))
    parts.append("админка: " + ", ".join(prof.get("admin", [])))
    parts.append("поле входа: " + str(prof.get("login_field")))

    parts.append(_sec("параметры для проверки"))
    for path, param, val in prof.get("params", []):
        parts.append("%s  %s=%s" % (path, param, val))

    try:
        got = mods.list_mods(host) or []
        parts.append(_sec("сторонние модули") + (", ".join(got) or "нет"))
    except Exception:
        pass

    try:
        files.run(host, kind)
        dump = os.path.join(config.LOGS, host + "_files.txt")
        if os.path.isfile(dump):
            with open(dump, encoding="utf-8", errors="ignore") as f:
                lines = [l.rstrip() for l in f if " 200 " in l or l.startswith("200")]
            parts.append(_sec("найденные файлы (%d)" % len(lines)))
            parts.append("\n".join(lines[:120]))
    except Exception as e:
        parts.append(_sec("файлы") + "сбой: %s" % e)

    for path in ("/system/storage/logs/error.log", "/storage/logs/error.log",
                 "/wp-content/debug.log", "/storage/logs/laravel.log"):
        try:
            r = http.get(host, path, timeout=20)
        except Exception:
            continue
        if r.status_code == 200 and len(r.text) > 50:
            parts.append(_sec("хвост лога " + path))
            parts.append("\n".join(r.text.splitlines()[-40:]))

    parts.append(_sec("формы входа"))
    for p in prof.get("admin", []):
        try:
            r = http.get(host, p, timeout=20)
            low = r.text.lower()
            field = prof.get("login_field") or "username"
            mark = "форма входа" if ('name="%s"' % field) in low else "поля нет"
            parts.append("%s -> %d, %s, размер %d, финал %s"
                         % (p, r.status_code, mark, len(r.content), r.url))
        except Exception as e:
            parts.append("%s -> сбой %s" % (p, e))

    try:
        hits = bypass.extras(host, [kind])
        if hits:
            parts.append(_sec("обходы"))
            for path, kk, body in hits:
                parts.append("%s [%s] %s" % (path, kk, " ".join(body.split())[:200]))
    except Exception:
        pass

    for fn, name, limit in ((subdom.run, "поддомены", 60), (arch.run, "архивы", 60)):
        try:
            got = fn(host) or []
            parts.append(_sec(name + " (%d)" % len(got)))
            for x in got[:15]:
                parts.append(str(x))
        except Exception as e:
            parts.append(_sec(name) + "сбой: %s" % e)

    out = os.path.join(DOSSIER, host + ".txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    try:
        state.set_status(host, "dossier", note="досье собрано")
    except Exception:
        pass
    return out


def run(host):
    ui.say("собираю досье, это может занять минуту")
    p = build(host)
    size = os.path.getsize(p)
    with open(p, encoding="utf-8") as f:
        body = f.read()
    secs = [l.strip("= ") for l in body.splitlines() if l.startswith("=== ")]
    ui.ok("досье: %s (%d байт)" % (p, size))
    ui.say("разделы: " + ", ".join(secs))
    return p


if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else ""
    if not h:
        print("укажи домен")
        sys.exit(1)
    print(run(h))
