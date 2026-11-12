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
                   ("/index.php?route=product/search", "search", "a"),
                   ("/index.php?route=product/category", "sort", "p.price"),
                   ("/index.php?route=product/category", "order", "ASC"),
                   ("/index.php?route=product/category", "limit", "20"),
                   ("/index.php?route=product/category", "page", "2")],
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
        "params": [("/search/", "q", "a"), ("/catalog/", "SECTION_ID", "1"),
                   ("/catalog/", "ELEMENT_ID", "1"), ("/catalog/", "PAGEN_1", "1"),
                   ("/bitrix/admin/sale_order.php", "ID", "1")],
        "login_field": "USER_LOGIN",
    },
    "prestashop": {
        "files": ["/config/settings.inc.php", "/app/config/parameters.php",
                  "/app/config/parameters.yml", "/.env", "/.git/config",
                  "/adminer.php", "/phpmyadmin/"],
        "admin": ["/admin/", "/admin123/"],
        "params": [("/", "s", "a"), ("/", "id_product", "1"),
                   ("/", "id_category", "2"), ("/", "orderby", "price"),
                   ("/", "id_lang", "1")],
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
    "joomla": {
        "files": ["/configuration.php", "/configuration.php~", "/configuration.php.bak",
                  "/administrator/manifests/files/joomla.xml", "/administrator/",
                  "/.env", "/.git/config", "/backup.sql", "/dump.sql"],
        "admin": ["/administrator/", "/administrator/index.php"],
        "params": [("/", "searchword", "a"),
                   ("/index.php?option=com_content&view=article", "id", "1"),
                   ("/index.php?option=com_content&view=category", "id", "2"),
                   ("/index.php?option=com_content&view=category", "catid", "2"),
                   ("/index.php?option=com_finder&view=search", "q", "a"),
                   ("/index.php?option=com_tags&view=tag", "id", "1")],
        "login_field": "username",
    },
    "dle": {
        "files": ["/engine/data/config.php", "/engine/data/dbconfig.php",
                  "/admin.php", "/backup/", "/.env", "/.git/config"],
        "admin": ["/admin.php"],
        "params": [("/index.php?do=search&subaction=search", "story", "a"),
                   ("/index.php?subaction=showfull", "id", "1"),
                   ("/index.php?do=stats", "id", "1"),
                   ("/index.php?do=feedback", "id", "1")],
        "login_field": "login_name",
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
