# -*- coding: utf-8 -*-
"""Признаки настоящего содержимого, чтобы не считать находкой пустышку."""

RULES = [
    ("config", ("DB_PASSWORD", "DB_NAME", "define(")),
    ("env", ("APP_KEY", "APP_ENV", "DB_PASSWORD", "DB_HOST", "MAIL_HOST")),
    ("log", ("PHP Fatal", "Stack trace", "PHP Warning", "2026-", "2025-")),
    ("sql", ("INSERT INTO", "CREATE TABLE", "-- MySQL")),
    ("adminer", ("adminer", "loginForm")),
    ("pma", ("phpMyAdmin", "pma_username")),
    ("install", ("install", "database")),
    ("git", ("[core]", "ref:", "repositoryformatversion")),
    ("status", ("Apache Server Status", "requests currently being processed")),
    ("config-dist", ("DB_PASSWORD", "DB_NAME", "define(")),
]

STRONG = ("DB_PASSWORD", "DB_NAME", "APP_KEY", "APP_ENV", "[core]",
          "repositoryformatversion", "PHP Fatal", "Stack trace",
          "pma_username", "loginForm")


def real(path, body):
    if not body or len(body) < 40:
        return False
    low = body.lower()
    for name, keys in RULES:
        if name in path.lower():
            return any(k.lower() in low for k in keys)
    return any(k.lower() in low for k in STRONG)
