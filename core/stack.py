# -*- coding: utf-8 -*-
from core import browser

MARKS = {
    "laravel": ("laravel_session", "xsrf-token"),
    "opencart": ("ocsessid", "oc_session", "oc_currency"),
    "wordpress": ("wordpress_", "wp-settings"),
    "bitrix": ("bitrix_",),
    "django": ("csrftoken", "sessionid"),
    "php": ("phpsessid",),
}


def guess(host):
    st = browser.load_state(host)
    names = " ".join((c.get("name") or "").lower() for c in st.get("cookies", []))
    tags = set()
    for tag, keys in MARKS.items():
        for k in keys:
            if k in names:
                tags.add(tag)
    return tags
