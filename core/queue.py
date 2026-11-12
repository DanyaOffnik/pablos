# -*- coding: utf-8 -*-
import os

from core import config


def _read(path):
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            h = line.strip().lower().split("/")[0]
            if "." in h and " " not in h and h not in out:
                out.append(h)
    return out


def _write(path, hosts):
    with open(path, "w", encoding="utf-8") as f:
        for h in hosts:
            f.write(h + "\n")


def queue():
    return _read(config.LIST)


def done():
    return _read(config.DONE)


def trash():
    return _read(config.TRASH)


def seen():
    return set(queue()) | set(done()) | set(trash())


def add(hosts):
    host = [h.strip().lower() for h in hosts if h.strip()]
    q = queue()
    for h in host:
        if h not in q:
            q.append(h)
    _write(config.LIST, q)


def drop(host, where="done"):
    host = host.strip().lower()
    q = [h for h in queue() if h != host]
    _write(config.LIST, q)
    path = config.DONE if where == "done" else config.TRASH
    lst = _read(path)
    if host not in lst:
        lst.append(host)
    _write(path, lst)


def drop_hot(host, where="done"):
    drop(host, where)


def add_hot(host):
    """Пометить годным: из очереди в отработанные."""
    drop(host, "done")


def restore(host):
    host = host.strip().lower()
    for path in (config.DONE, config.TRASH):
        lst = _read(path)
        if host in lst:
            _write(path, [h for h in lst if h != host])
    add([host])
