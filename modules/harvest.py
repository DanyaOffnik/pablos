# -*- coding: utf-8 -*-
import os
import random
import re
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from core import config, http, queue, state, ui

HREF = re.compile(r"uddg=([^&\"]+)")
BING = re.compile(r'href="(https?://[^"]+)"')

COUNTRIES = {
    "ua": ((".ua", ".com.ua", ".net.ua", ".org.ua", ".kiev.ua", ".in.ua"),
           ["киев", "львов", "харьков", "днепр", "одесса", "винница", "луцк",
            "ровно", "тернополь", "ужгород", "черновцы", "житомир", "запорожье"]),
    "kz": ((".kz", ".com.kz", ".org.kz"),
           ["алматы", "астана", "шымкент", "караганда", "актобе", "павлодар"]),
    "by": ((".by", ".com.by"), ["минск", "гомель", "брест", "витебск", "гродно", "могилев"]),
    "ru": ((".ru", ".com.ru", ".msk.ru", ".spb.ru"),
           ["москва", "спб", "новосибирск", "екатеринбург", "казань", "самара"]),
    "kg": ((".kg", ".com.kg"), ["бишкек", "ош"]),
    "uz": ((".uz", ".com.uz"), ["ташкент", "самарканд"]),
    "md": ((".md",), ["кишинев"]),
    "am": ((".am",), ["ереван"]),
    "ge": ((".ge", ".com.ge"), ["тбилиси"]),
    "az": ((".az", ".com.az"), ["баку"]),
}

WORDS = ["ткани", "посуда", "мебель", "инструмент", "зоотовары", "косметика",
         "детские товары", "сантехника", "электрика", "спецодежда", "семена",
         "стройматериалы", "подарки", "бытовая техника", "аксессуары",
         "канцтовары", "спорттовары", "автозапчасти", "двери", "плитка"]

BRANDS = ["оптом", "недорого", "интернет-магазин", "купить", "доставка", "цена"]

ENGQ = {
    "opencart": ['"index.php?route=product/category"', '"index.php?route=product/product"',
                 "ocstore", "opencart магазин"],
    "wordpress": ['"wp-content/themes" магазин', '"wp-json" магазин', "wordpress магазин"],
    "bitrix": ['"bitrix/catalog"', "bitrix магазин"],
    "prestashop": ['"id_product" магазин', "prestashop магазин"],
}

MARKS = (
    ("wordpress", ("wp-content", "wp-includes", "wp-json")),
    ("opencart", ("route=product", "catalog/view", "oc_")),
    ("bitrix", ("bitrix",)),
    ("prestashop", ("prestashop", "id_product")),
)

CF = ("just a moment", "one moment, please", "checking your browser",
      "cf-browser-verification")


def _norm(url, tails):
    try:
        net = urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""
    if net.startswith("www."):
        net = net[4:]
    if net.count(".") < 1 or not any(net.endswith(t) for t in tails):
        return ""
    return net


def _probe(host):
    try:
        r = http.get(host, "/", timeout=10)
    except Exception:
        return "нет связи"
    low = r.text[:3000].lower()
    if r.status_code in (403, 503) or any(c in low for c in CF):
        return "защита"
    if r.status_code != 200:
        return "код %d" % r.status_code
    body = r.text[:120000].lower()
    for name, keys in MARKS:
        for k in keys:
            if k in body:
                return name
    return "неизвестно"


def _queries(zones, kinds, n):
    cities = [c for z in zones for c in COUNTRIES[z][1]]
    words = list(WORDS)
    random.shuffle(words)
    out = []
    seen = set()
    for i in range(n * 3):
        if len(out) >= n:
            break
        q = "%s %s %s %s" % (random.choice(ENGQ[random.choice(kinds)]),
                             random.choice(words), random.choice(BRANDS),
                             random.choice(cities))
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def _fetch(q, tails):
    got = []
    try:
        r = http.get("html.duckduckgo.com", "/html/?q=" + urllib.parse.quote(q), timeout=15)
        for m in HREF.findall(r.text):
            h = _norm(urllib.parse.unquote(m), tails)
            if h:
                got.append(h)
    except Exception:
        pass
    if len(got) < 5:
        for page in (1, 51):
            try:
                r = http.get("www.bing.com", "/search?q=" + urllib.parse.quote(q)
                             + "&count=50&first=%d" % page, timeout=15)
                for m in BING.findall(r.text):
                    h = _norm(m, tails)
                    if h and "bing.com" not in h and "microsoft" not in h:
                        got.append(h)
            except Exception:
                break
            time.sleep(0.8)
    return got


def run():
    ui.say("страны: ua, kz, by, ru, kg, uz, md, am, ge, az")
    zones = [z.strip() for z in ui.ask("какие берём", "ua,kz,by").split(",")
             if z.strip() in COUNTRIES]
    ui.say("движки: opencart, wordpress, bitrix, prestashop")
    kinds = [k.strip() for k in ui.ask("какие берём", "opencart,wordpress").split(",")
             if k.strip() in ENGQ]
    if not zones or not kinds:
        ui.say("ничего не выбрано")
        return
    try:
        n = max(1, min(60, int(ui.ask("сколько запросов", "16"))))
    except Exception:
        n = 16

    tails = tuple(t for z in zones for t in COUNTRIES[z][0])
    queries = _queries(zones, kinds, n)
    log = os.path.join(config.DATA, "queries.txt")
    with open(log, "a", encoding="utf-8") as f:
        for q in queries:
            f.write(q + "\n")

    known = queue.seen()
    found = set()
    done = [0]

    def work(q):
        got = _fetch(q, tails)
        fresh = []
        for h in got:
            if h not in known:
                known.add(h)
                fresh.append(h)
        done[0] += 1
        ui.say("%-44s +%d" % (q[:44], len(fresh)))
        return fresh

    with ThreadPoolExecutor(max_workers=4) as pool:
        for fresh in pool.map(work, queries):
            found.update(fresh)

    if not found:
        ui.say("новых доменов нет")
        return

    found = list(found)
    ui.say("проверяю %d найденных" % len(found))
    clean, blocked, alien = [], [], []
    with ThreadPoolExecutor(max_workers=16) as pool:
        for host, tag in zip(found, pool.map(_probe, found)):
            if tag == "защита":
                blocked.append(host)
            elif tag in kinds:
                clean.append(host)
            else:
                alien.append(host)

    queue.add(clean)
    for h in clean:
        state.put(h)
    for name, lst in (("cf.txt", blocked), ("alien.txt", alien)):
        if not lst:
            continue
        path = os.path.join(config.DATA, name)
        old = set()
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                old = {x.strip() for x in f if x.strip()}
        with open(path, "a", encoding="utf-8") as f:
            for h in lst:
                if h not in old:
                    f.write(h + "\n")

    ui.ok("в очередь: %d" % len(clean))
    ui.say("защита: %d, чужие движки: %d" % (len(blocked), len(alien)))
    ui.say("запросы записаны в " + log)
