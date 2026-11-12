# -*- coding: utf-8 -*-
"""nuclei -> шаблоны. Парсинг один раз в индекс, конвертация из индекса.

  python -m modules.nuc --index
  python -m modules.nuc wordpress bitrix
  python -m modules.nuc --prune
"""
import collections
import glob
import json
import os
import re
import sys

import yaml

from core import config

SRC = r"C:\work\nuclei\nuclei-templates-main"
OUT = os.path.join(config.DATA, "templates")
INDEX = r"C:\work\nuclei\index.jsonl"
SKIP_DIR = ("dns", "ssl", "file", "headless", "javascript", "cloud", "network", "workflows", "helpers")
ENGINES = ("opencart", "prestashop", "bitrix", "wordpress", "joomla", "drupal", "magento")
SEV = {"critical": 8, "high": 6, "medium": 4, "low": 3, "info": 2}
CAP = 30
REASONS = collections.Counter()
FINGER = collections.Counter()
SEEN = set()
USED = set()


def _engine(blob):
    low = blob.lower()
    for name in ENGINES:
        if name in low:
            return name
    return ""


def _clean(path):
    for junk in ("{{BaseURL}}", "{{RootURL}}", "{{Hostname}}", "{{Host}}"):
        path = path.replace(junk, "")
    path = path.strip()
    if path and not path.startswith("/"):
        path = "/" + path
    return path


def _values(v):
    """Список значений или путь к словарю внутри nuclei."""
    if isinstance(v, list):
        return [str(x) for x in v], False
    if isinstance(v, str) and v:
        p = v if os.path.isabs(v) else os.path.join(SRC, v)
        try:
            lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
        except Exception:
            return [], True
        got = [x.strip() for x in lines if x.strip() and not x.strip().startswith("#")]
        return got[:CAP], True
    return [], False


def _matcher(req):
    picked = None
    only_status = True
    for m in req.get("matchers") or []:
        if m.get("negative"):
            continue
        t = m.get("type")
        if t == "status":
            v = m.get("status") or []
            if v and not picked:
                picked = {"type": "status", "value": int(str(v[0]))}
            continue
        only_status = False
        if picked:
            continue
        if t == "word":
            v = m.get("words") or []
            if v:
                picked = {"type": "body", "value": str(v[0])}
        elif t == "regex":
            v = m.get("regex") or []
            if v:
                picked = {"type": "regex", "value": str(v[0])}
        elif t == "dsl":
            d = " ".join(map(str, m.get("dsl") or []))
            mm = re.search(r"contains\((?:\w+)?body,\s*[\"'](.+?)[\"']\)", d)
            if mm:
                picked = {"type": "body", "value": mm.group(1)}
            elif "duration" in d:
                mm = re.search(r"(\d+)", d)
                picked = {"type": "time", "value": int(mm.group(1)) if mm else 4}
            else:
                mm = re.search(r"status_code\s*==\s*(\d+)", d)
                if mm:
                    picked = {"type": "status", "value": int(mm.group(1))}
    return picked, only_status


def build_index():
    n = 0
    with open(INDEX, "w", encoding="utf-8") as out:
        for p in glob.glob(os.path.join(SRC, "http", "**", "*.yaml"), recursive=True):
            rel = os.path.relpath(p, SRC)
            if any(s in rel.split(os.sep) for s in SKIP_DIR):
                continue
            try:
                doc = yaml.safe_load(open(p, encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(doc, dict):
                continue
            tags = doc.get("tags") or []
            if isinstance(tags, str):
                tags = tags.split(",")
            info = doc.get("info") or {}
            eng = _engine(rel + " " + " ".join(map(str, tags)) + " " + str(info.get("name", "")))
            if not eng:
                continue
            http = doc.get("http") or doc.get("requests")
            if not isinstance(http, list) or not http or not isinstance(http[0], dict):
                continue
            req = http[0]
            body = str(req.get("body") or "")
            method = (req.get("method") or "").upper()
            if req.get("path"):
                path = str(req["path"][0])
            elif req.get("raw"):
                lines = []
                for x in req["raw"]:
                    lines.extend(str(x).splitlines())
                if not lines:
                    continue
                first = lines[0].split()
                if len(first) < 2:
                    continue
                method = method or first[0].upper()
                path = first[1]
                for i, ln in enumerate(lines[1:], 1):
                    if not ln.strip():
                        body = "\n".join(lines[i + 1:])
                        break
            else:
                continue
            m, only_status = _matcher(req)
            if not m:
                continue
            out.write(json.dumps({
                "rel": rel, "engine": eng, "path": _clean(path),
                "body": body,
                "method": method,
                "payloads": req.get("payloads") or {},
                "match": m, "only_status": only_status,
                "severity": str(info.get("severity", "medium")).lower(),
                "name": str(info.get("name", ""))[:80],
            }, ensure_ascii=False) + "\n")
            n += 1
    return n


def _tid(engine, rel):
    base = "nuc-%s-%s" % (engine, re.sub(r"[^a-z0-9.-]+", "-", os.path.basename(rel)[:-5].lower()))
    tid = base
    i = 2
    while tid in USED or os.path.exists(os.path.join(OUT, tid + ".json")):
        tid = "%s-%d" % (base, i)
        i += 1
    USED.add(tid)
    return tid


def convert(engine, limit=0):
    if not os.path.exists(INDEX):
        print("нет индекса, сначала: python -m modules.nuc --index")
        return 0
    cand = []
    for line in open(INDEX, encoding="utf-8"):
        rec = json.loads(line)
        if rec["engine"] != engine:
            continue
        path, body = rec["path"], rec["body"]
        payloads = rec["payloads"]
        if not payloads:
            REASONS["нет payloads"] += 1
            continue
        names = list(payloads.keys())
        var = names[0]
        values, wl = _values(payloads[var])
        if not values:
            REASONS["payload не разрешился"] += 1
            continue
        for extra in names[1:]:
            ev, _ = _values(payloads.get(extra))
            if ev:
                path = path.replace("{{%s}}" % extra, str(ev[0]))
                body = body.replace("{{%s}}" % extra, str(ev[0]))
        ph = "{{%s}}" % var
        in_path = ph in path
        in_body = ph in body
        finger = False
        if not in_path and not in_body:
            if not values or FINGER[engine] >= 80:
                REASONS["payload без места подстановки"] += 1
                continue
            finger = True
            FINGER[engine] += 1
        if in_path:
            path = path.replace(ph, "{{p}}")
        if "{{" in (path.replace("{{p}}", "") + body.replace(ph, "")):
            REASONS["чужая переменная"] += 1
            continue

        m = rec["match"]
        weak = False
        if rec["only_status"]:
            if re.search(r"\.[a-z0-9]{2,5}($|\?|\{\{)", path) or m.get("value") in (301, 302, 403):
                weak = True
            else:
                REASONS["статус без специфики"] += 1
                continue

        method = rec["method"] or ("POST" if in_body else "GET")
        key = (method, path, tuple(str(v) for v in values))
        if key in SEEN:
            REASONS["дубль"] += 1
            continue
        SEEN.add(key)

        sev = rec["severity"]
        t = {
            "id": _tid(engine, rec["rel"]),
            "engine": engine, "method": method, "path": path,
            "payloads": [""] if finger else values,
            "match": m,
            "score": 3 if finger else (max(3, SEV.get(sev, 4) - 3) if weak else max(3, SEV.get(sev, 4))),
            "note": "nuclei: " + rec["name"] + ((" | версии: " + ", ".join(values[:4])) if finger else ""),
        }
        if finger:
            t["finger"] = True
        if weak:
            t["weak"] = True
        if wl:
            t["wordlist"] = True
        if in_body:
            t["where"] = "post-json" if body.lstrip()[:1] in ("{", "[") else "post-form"
            t["param"] = var
            t["body_tpl"] = body.replace(ph, "{{p}}")
        cand.append(t)
    cand.sort(key=lambda x: -x["score"])
    made = 0
    for t in cand:
        if limit and made >= limit:
            break
        json.dump(t, open(os.path.join(OUT, t["id"] + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        made += 1
    return made


def prune():
    killed = collections.Counter()
    seen = set()
    for p in sorted(glob.glob(os.path.join(OUT, "nuc-*.json"))):
        try:
            t = json.load(open(p, encoding="utf-8"))
        except Exception:
            os.remove(p); killed["битый json"] += 1; continue
        path = t.get("path", "")
        m = t.get("match") or {}
        reason = ""
        if "{{p}}" not in path and not t.get("body_tpl") and not t.get("finger"):
            reason = "нет payload"
        elif not path.startswith("/"):
            reason = "путь без слэша"
        elif "{{" in path.replace("{{p}}", ""):
            reason = "чужая переменная"
        else:
            key = (t.get("method"), path, tuple(t.get("payloads") or []))
            if key in seen:
                reason = "дубль"
            seen.add(key)
        if reason:
            os.remove(p); killed[reason] += 1
    return killed


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] == "--index":
        print("проиндексировано", build_index())
    elif args and args[0] == "--prune":
        k = prune()
        print("вычищено", sum(k.values()), dict(k))
        print("осталось", len(glob.glob(os.path.join(OUT, "nuc-*.json"))))
    elif not args:
        print("укажи --index, --prune или движки")
    else:
        for eng in args:
            REASONS.clear(); SEEN.clear(); FINGER.clear()
            print("%-12s %d  %s" % (eng, convert(eng), dict(REASONS)))
