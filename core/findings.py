# -*- coding: utf-8 -*-
"""Единый формат находки. Находка без URL — не находка."""
import hashlib
import time


def make(host, url, tag, status=0, size=0, base_size=0, body="", payload="", extra=""):
    return {
        "host": host,
        "url": url,
        "tag": tag,
        "status": status,
        "size": size,
        "base_size": base_size,
        "sha1": hashlib.sha1((body or "")[:200000].encode("utf-8", "ignore")).hexdigest()[:12],
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "payload": payload,
        "extra": extra,
    }


def line(f):
    return " | ".join((f["ts"], f["host"], f["tag"], str(f["status"]),
                       str(f["size"]), f["url"], f["sha1"]))


def human(f):
    return "%s %s [%d] %s" % (f["tag"], f["url"], f["status"], f["sha1"])
