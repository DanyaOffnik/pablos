# -*- coding: utf-8 -*-
"""Классификация защиты хоста и стратегия работы с ним."""
import json
import os
import time

from core import config, http

DB = os.path.join(config.DATA, "waf.json")

SIGNS = (
    ("imunify", ("one moment, please", "just a moment", "window.location.reload()",
                 "/z0f76a1d1"), "browser"),
    ("ddosguard", ("__ddg", 'content="0; url=https://', "attempt="), "browser"),
    ("gas_shield", ("gas shield",), "browser"),
    ("limiter", ("доступ временно ограничен", "vp_admin_tools", "sensitive_path"), "wait"),
    ("modsec", ("mod_security", "not acceptable"), "browser"),
)


def _load():
    try:
        with open(DB, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(host, data):
    db = _load()
    data["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    db[host] = data
    try:
        os.makedirs(os.path.dirname(DB), exist_ok=True)
        with open(DB, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def known(host):
    return _load().get(host)


def detect(host, timeout=8):
    """Возвращает {kind, strategy, note}. strategy: ok | browser | wait | skip."""
    res = {"kind": "", "strategy": "ok", "note": ""}
    try:
        r = http.get(host, "/", timeout=timeout)
    except Exception:
        res.update(kind="dead", strategy="skip", note="нет связи")
        _save(host, res)
        return res

    blob = (r.text[:8000] + " " + str(r.headers)).lower()
    if r.status_code == 429:
        res.update(kind="limiter", strategy="wait", note="429 лимит")
        _save(host, res)
        return res
    for kind, marks, strategy in SIGNS:
        for m in marks:
            if m in blob:
                res.update(kind=kind, strategy=strategy, note="защита: " + kind)
                _save(host, res)
                return res

    # блок кавычки: 200 без неё, 403 с ней
    try:
        a = http.get(host, "/?a=x", timeout=timeout)
        b = http.get(host, "/?a=%27", timeout=timeout)
        if a.status_code == 200 and b.status_code == 403:
            res.update(kind="quote_block", strategy="ok", note="кавычка закрыта")
    except Exception:
        pass

    _save(host, res)
    return res
