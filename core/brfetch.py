# -*- coding: utf-8 -*-
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core import browser, config

def main():
    if len(sys.argv) < 2:
        print("укажи домен")
        return
    host = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""
    st = browser._auto_body(host, url, 12)
    out = os.path.join(config.SESS, host + ".auto.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False)
    print("ok")


if __name__ == "__main__":
    main()
