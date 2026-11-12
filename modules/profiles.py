# -*- coding: utf-8 -*-
"""Профили движков: пути, параметры, признаки админки."""

PROFILES = {
    "opencart": {
        "files": ["/config.php", "/config-dist.php", "/admin/config.php",
                  "/config.php~", "/config.php.bak", "/config.php.save",
                  "/system/storage/logs/error.log", "/storage/logs/error.log",
                  "/.env", "/.env.bak", "/.git/config", "/backup.sql",
                  "/dump.sql", "/adminer.php", "/phpmyadmin/"],
        "admin": ["/admin/", "/admin/index.php?route=common/login"],
        "params": [("/index.php?route=product/product", "product_id", "1"),
                   ("/index.php?route=product/category", "path", "20"),
                   ("/index.php?route=product/search", "search", "a")],
        "login_field": "username",
    },
    "wordpress": {
        "files": ["/wp-config.php", "/wp-config.php.bak", "/wp-config.php~",
                  "/wp-config.php.save", "/wp-content/debug.log",
                  "/wp-content/uploads/", "/.env", "/.git/config",
                  "/backup.sql", "/dump.sql", "/adminer.php", "/phpmyadmin/"],
        "admin": ["/wp-login.php", "/wp-admin/"],
        "params": [("/", "s", "a"), ("/", "p", "1"), ("/", "cat", "1"),
                   ("/", "author", "1")],
        "login_field": "log",
    },
    "bitrix": {
        "files": ["/.env", "/bitrix/.settings.php", "/bitrix/php_interface/dbconn.php",
                  "/bitrix/.settings.php.bak", "/.git/config", "/backup.sql",
                  "/adminer.php", "/phpmyadmin/"],
        "admin": ["/bitrix/admin/"],
        "params": [("/search/", "q", "a"), ("/catalog/", "SECTION_ID", "1")],
        "login_field": "USER_LOGIN",
    },
    "prestashop": {
        "files": ["/config/settings.inc.php", "/app/config/parameters.php",
                  "/app/config/parameters.yml", "/.env", "/.git/config",
                  "/adminer.php", "/phpmyadmin/"],
        "admin": ["/admin/", "/admin123/"],
        "params": [("/", "s", "a"), ("/", "id_product", "1")],
        "login_field": "email",
    },
    "laravel": {
        "files": ["/.env", "/.env.bak", "/storage/logs/laravel.log",
                  "/bootstrap/cache/config.php", "/.git/config",
                  "/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php"],
        "admin": ["/admin/", "/login"],
        "params": [("/", "q", "a"), ("/", "id", "1")],
        "login_field": "email",
    },
    "frappe": {
        "files": ["/api/method/ping", "/files/", "/private/files/",
                  "/api/method/frappe.client.get_list?doctype=User"],
        "admin": ["/login", "/app"],
        "params": [("/login", "usr", "Administrator")],
        "login_field": "usr",
    },
    "django": {
        "files": ["/.env", "/.git/config", "/backup.sql", "/adminer.php"],
        "admin": ["/admin/", "/admin/login/"],
        "params": [("/", "q", "a"), ("/", "page", "1")],
        "login_field": "username",
    },
}

DEFAULT = "opencart"


def get(kind):
    return PROFILES.get(kind) or PROFILES[DEFAULT]
