# -*- coding: utf-8 -*-
"""Поиск доменов по движкам. Две выдачи, глубина по страницам, отсев парковок."""
import os
import random
import re
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from core import config, http, queue, state, ui

DDG = re.compile(r"uddg=([^&\"]+)")
BING = re.compile(r'href="(https?://[^"]+)"')
YANDEX = re.compile(r'href="(https?://[^"]+)"')

COUNTRIES = {
    "ua": ((".ua", ".com.ua", ".net.ua", ".org.ua", ".kiev.ua", ".in.ua"),
           ["киев", "львов", "харьков", "днепр", "одесса", "винница", "луцк",
            "ровно", "тернополь", "ужгород", "черновцы", "житомир", "запорожье",
            "ивано-франковск", "кривой рог", "николаев", "сумы", "черкассы"]),
    "kz": ((".kz", ".com.kz", ".org.kz"),
           ["алматы", "астана", "шымкент", "караганда", "актобе", "павлодар",
            "атырау", "костанай", "тараз", "усть-каменогорск"]),
    "by": ((".by", ".com.by"), ["минск", "гомель", "брест", "витебск", "гродно", "могилев"]),
    "ru": ((".ru", ".com.ru", ".msk.ru", ".spb.ru"),
           ["москва", "спб", "новосибирск", "екатеринбург", "казань", "самара",
            "нижний новгород", "челябинск", "омск", "ростов-на-дону", "уфа",
            "красноярск", "воронеж", "пермь", "волгоград"]),
    "kg": ((".kg", ".com.kg"), ["бишкек", "ош"]),
    "uz": ((".uz", ".com.uz"), ["ташкент", "самарканд", "бухара", "андижан"]),
    "md": ((".md",), ["кишинев", "белць", "тирасполь"]),
    "am": ((".am",), ["ереван", "гюмри"]),
    "ge": ((".ge", ".com.ge"), ["тбилиси", "батуми", "кутаиси"]),
    "az": ((".az", ".com.az"), ["баку", "гянджа"]),
}

WORDS = ["ткани", "посуда", "мебель", "инструмент", "зоотовары", "косметика",
         "детские товары", "сантехника", "электрика", "спецодежда", "семена",
         "стройматериалы", "подарки", "бытовая техника", "аксессуары",
         "канцтовары", "спорттовары", "автозапчасти", "двери", "плитка",
         "обои", "люстры", "ковры", "текстиль", "посуда оптом", "хозтовары"]

BRANDS = ["оптом", "недорого", "интернет-магазин", "купить", "доставка", "цена",
          "каталог", "распродажа"]

ENGQ = {
    "opencart": ['"index.php?route=product/category"', '"index.php?route=product/product"',
                 "ocstore", "opencart магазин"],
    "wordpress": ['"wp-content/themes" магазин', '"wp-json" магазин', "wordpress магазин"],
    "bitrix": ['"bitrix/catalog"', "bitrix магазин"],
    "prestashop": ['"id_product" магазин', "prestashop магазин"],
    "joomla": ['"option=com_content"', '"com_content&view=article"', "joomla сайт"],
    "dle": ['"DataLife Engine"', '"engine/data/config.php"', "datalife движок"],
    "frappe": ['"api/method/ping"', "frappe crm"],
    "laravel": ['"_ignition/health-check"', "laravel сайт"],
    "django": ['"csrfmiddlewaretoken" сайт', "django сайт"],
}

MARKS = (
    ("wordpress", ("wp-content", "wp-includes", "wp-json")),
    ("opencart", ("route=product", "catalog/view", "oc_")),
    ("bitrix", ("bitrix",)),
    ("prestashop", ("prestashop", "id_product")),
    ("joomla", ("com_content", "/media/system/js/", "joomla")),
    ("dle", ("datalife", "engine/classes/")),
    ("frappe", ("/assets/frappe/", "frappe")),
    ("laravel", ("laravel", "csrf-token")),
    ("django", ("csrfmiddlewaretoken",)),
)

CF = ("just a moment", "one moment, please", "checking your browser",
      "cf-browser-verification", "ddos-guard", "imunify")
PARK = ("domain is for sale", "купить домен", "parked", "sedoparking",
        "данный домен", "домен продается", "this domain", "hugedomains")
DEAD = ("нет связи",)


def _norm(url, tails):
    try:
        net = urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""
    if net.startswith("www."):
        net = net[4:]
    if net.count(".") < 1 or not any(net.endswith(t) for t in tails):
        return ""
    if any(x in net for x in ("bing.", "duckduckgo.", "yandex.", "google.",
                              "microsoft.", "wikipedia.", "youtube.")):
        return ""
    return net


def _probe(host):
    try:
        r = http.get(host, "/", timeout=10)
    except Exception:
        return "нет связи"
    low = r.text[:4000].lower()
    if any(c in low for c in PARK):
        return "парковка"
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
    guard = 0
    while len(out) < n and guard < n * 8:
        guard += 1
        q = "%s %s %s %s" % (random.choice(ENGQ[random.choice(kinds)]),
                             random.choice(words), random.choice(BRANDS),
                             random.choice(cities))
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def _ddg(q, tails):
    got = []
    try:
        r = http.get("html.duckduckgo.com", "/html/?q=" + urllib.parse.quote(q), timeout=15)
        for m in DDG.findall(r.text):
            h = _norm(urllib.parse.unquote(m), tails)
            if h:
                got.append(h)
    except Exception:
        pass
    return got


def _bing(q, tails, pages=(1, 11, 21, 31)):
    got = []
    for first in pages:
        try:
            r = http.get("www.bing.com",
                         "/search?q=" + urllib.parse.quote(q)
                         + "&count=30&first=%d" % first, timeout=15)
        except Exception:
            break
        before = len(got)
        for m in BING.findall(r.text):
            h = _norm(m, tails)
            if h:
                got.append(h)
        if len(got) == before:
            break
        time.sleep(0.6)
    return got


def _fetch(q, tails):
    """Два источника; если первый дал мало — второй глубже."""
    got = _ddg(q, tails)
    if len(got) < 8:
        got += _bing(q, tails)
    else:
        got += _bing(q, tails, pages=(1,))
    seen = []
    for h in got:
        if h not in seen:
            seen.append(h)
    return seen


def run():
    ui.say("страны: " + ", ".join(COUNTRIES))
    zones = [z.strip() for z in ui.ask("какие берём", "ua,kz,by").split(",")
             if z.strip() in COUNTRIES]
    ui.say("движки: " + ", ".join(ENGQ))
    kinds = [k.strip() for k in ui.ask("какие берём", "opencart,wordpress").split(",")
             if k.strip() in ENGQ]
    if not zones or not kinds:
        ui.say("ничего не выбрано")
        return
    try:
        n = max(1, min(120, int(ui.ask("сколько запросов", "24"))))
    except Exception:
        n = 24
    try:
        th = max(1, min(8, int(ui.ask("потоков поиска", "4"))))
    except Exception:
        th = 4

    tails = tuple(t for z in zones for t in COUNTRIES[z][0])
    queries = _queries(zones, kinds, n)
    log = os.path.join(config.DATA, "queries.txt")
    with open(log, "a", encoding="utf-8") as f:
        for q in queries:
            f.write(q + "\n")

    known = queue.seen()
    found = set()
    done = [0]
    lock_words = []

    def work(q):
        got = _fetch(q, tails)
        fresh = []
        for h in got:
            if h not in known:
                known.add(h)
                fresh.append(h)
        done[0] += 1
        ui.say("%-46s +%d" % (q[:46], len(fresh)))
        return fresh

    with ThreadPoolExecutor(max_workers=th) as pool:
        for fresh in pool.map(work, queries):
            found.update(fresh)

    if not found:
        ui.say("новых доменов нет")
        return

    found = list(found)
    ui.say("проверяю %d найденных" % len(found))
    clean, blocked, alien, parked = [], [], [], []
    with ThreadPoolExecutor(max_workers=16) as pool:
        for host, tag in zip(found, pool.map(_probe, found)):
            if tag == "защита":
                blocked.append(host)
            elif tag == "парковка":
                parked.append(host)
            elif tag in kinds:
                clean.append(host)
            else:
                alien.append(host)

    queue.add(clean)
    for h in clean:
        state.put(h)

    for name, lst in (("cf.txt", blocked), ("alien.txt", alien), ("parked.txt", parked)):
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
    ui.say("защита: %d, парковки: %d, чужие движки: %d" % (len(blocked), len(parked), len(alien)))
    ui.say("запросы записаны в " + log)
    if blocked:
        ui.say("защищённые лежат в data\\cf.txt — их можно взять позже")
