# -*- coding: utf-8 -*-
"""Сборка отчёта по каталогу прогона. Источник: findings.csv или findings_*.csv."""
import csv
import json
import os
import time

from core import ui


def _read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter=";")
        head = next(r, None) or []
        rows = [x for x in r if x]
    return [h.strip().lower() for h in head], rows


def _col(head, *names):
    for n in names:
        if n in head:
            return head.index(n)
    return -1


def _sources(d):
    if os.path.isfile(d):
        d = os.path.dirname(d)
    out = []
    for n in sorted(os.listdir(d)):
        low = n.lower()
        if low.endswith(".csv") and ("findings" in low or "mass" in low):
            out.append(os.path.join(d, n))
    return out


def _state(d):
    p = os.path.join(d, "state.json")
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def build(d):
    hosts = {}
    sources = _sources(d)
    if not sources:
        ui.say("в каталоге нет файлов находок")
        return ""

    for path in sources:
        head, rows = _read_csv(path)
        i_h = _col(head, "хост", "host")
        if i_h < 0:
            continue
        i_t = _col(head, "метка", "tag")
        i_u = _col(head, "url")
        i_c = _col(head, "код", "status")
        i_s = _col(head, "размер", "size")
        i_sc = _col(head, "баллы", "score")
        i_n = _col(head, "находки", "notes")
        i_cr = _col(head, "вход", "creds")
        for row in rows:
            if i_h >= len(row):
                continue
            h = row[i_h].strip().lower()
            if not h:
                continue
            e = hosts.setdefault(h, {"score": 0, "creds": "", "notes": [], "urls": []})
            if i_u >= 0 and i_u < len(row) and row[i_u].strip():
                e["urls"].append({"tag": row[i_t] if 0 <= i_t < len(row) else "",
                                  "url": row[i_u],
                                  "code": row[i_c] if 0 <= i_c < len(row) else "",
                                  "size": row[i_s] if 0 <= i_s < len(row) else ""})
            if i_t >= 0 and i_t < len(row) and row[i_t].strip():
                e["notes"].append(row[i_t])
            if i_sc >= 0 and i_sc < len(row):
                try:
                    e["score"] = max(e["score"], int(row[i_sc]))
                except Exception:
                    pass
            if i_n >= 0 and i_n < len(row) and row[i_n].strip():
                e["notes"] += [x.strip() for x in row[i_n].split(",") if x.strip()]
            if i_cr >= 0 and i_cr < len(row) and row[i_cr].strip():
                e["creds"] = row[i_cr].strip()

    st = _state(d) if isinstance(_state(d), dict) else {}
    for h, rec in st.items():
        e = hosts.setdefault(h, {"score": 0, "creds": "", "notes": [], "urls": []})
        e["score"] = max(e["score"], int(rec.get("score") or 0))
        if rec.get("creds"):
            e["creds"] = rec["creds"]
        e["notes"] += rec.get("notes") or []

    for e in hosts.values():
        e["notes"] = list(dict.fromkeys(n for n in e["notes"] if n))

    cracked = {h: e for h, e in hosts.items() if e["creds"]}
    hot = {h: e for h, e in hosts.items() if not e["creds"] and (e["urls"] or e["score"] >= 3)}
    junk = {h: e for h, e in hosts.items() if h not in cracked and h not in hot}

    out = os.path.join(d, "report.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Отчёт\n\n")
        f.write("каталог: `%s`\nсобран: %s\n\n" % (d, time.strftime("%Y-%m-%d %H:%M")))
        f.write("всего целей: %d · со входом: %d · с зацепками: %d · пустых: %d\n\n"
                % (len(hosts), len(cracked), len(hot), len(junk)))

        if cracked:
            f.write("## Входы\n\n")
            for h, e in sorted(cracked.items()):
                f.write("### %s\n\n- учётка: `%s`\n" % (h, e["creds"]))
                if e["notes"]:
                    f.write("- метки: %s\n" % ", ".join(e["notes"]))
                for u in e["urls"][:15]:
                    f.write("- `%s` %s %s %s\n" % (u["url"], u["tag"], u["code"], u["size"]))
                f.write("\n")

        if hot:
            f.write("## Зацепки\n\n")
            for h, e in sorted(hot.items(), key=lambda x: -x[1]["score"]):
                f.write("### %s  (баллы %d)\n\n" % (h, e["score"]))
                if e["notes"]:
                    f.write("- метки: %s\n" % ", ".join(e["notes"]))
                for u in e["urls"][:15]:
                    f.write("- `%s` %s %s %s\n" % (u["url"], u["tag"], u["code"], u["size"]))
                f.write("\n")

        if junk:
            f.write("## Пустые\n\n")
            f.write(", ".join(sorted(junk)) + "\n")

    return out


def run(d):
    p = build(d)
    if p:
        ui.ok("отчёт: " + p)
    return p
