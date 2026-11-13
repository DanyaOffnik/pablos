# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\modules\night.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """        if th:
            rec["notes"].append("шаблоны: %d" % len(th))
            score = min(12, score + min(4, sum(c for _, _, c in th) // 4))
            loud = [(i, p, c) for i, p, c in th if c >= 6]
            if loud:
                lvl = 2 if max(c for _, _, c in loud) >= 8 else 3
                notify.send_lvl(lvl, "ЗАЦЕПКИ\\n%s\\n%s" % (
                    host, "\\n".join("%s: %s" % (i, p[:40]) for i, p, _ in loud[:4])))"""
new = """        if th:
            rec["notes"].append("шаблоны: %d" % len(th))
            score = min(12, score + min(4, len(th) * 2))
            strong = ("x-bx-restore", "x-ps-parameters", "sqli", "x-wp-env",
                      "x-jm-config", "x-oc-dump", "x-fr-guest", "x-jm-users")
            loud = [f for f in th if str(f.get("tag", "")).startswith(strong)]
            if loud:
                lvl = 2 if len(loud) else 3
                notify.send_lvl(lvl, "ЗАЦЕПКИ\\n%s\\n%s" % (
                    host, "\\n".join("%s: %s" % (f.get("tag"), str(f.get("url"))[:60])
                                     for f in loud[:4])))"""
if s.count(old) != 1:
    print("шаблоны: блок не найден"); sys.exit(1)
s = s.replace(old, new)

old2 = """        if ah:
            rec["notes"].append("архив " + ah[0][1])
            notify.send_lvl(3, "АРХИВ\\n%s\\n%s" % (host, ah[0][0]))"""
new2 = """        if ah and isinstance(ah[0], (list, tuple)) and len(ah[0]) > 1:
            rec["notes"].append("архив " + str(ah[0][1]))
            notify.send_lvl(3, "АРХИВ\\n%s\\n%s" % (host, ah[0][0]))"""
if s.count(old2) != 1:
    print("архив: блок не найден"); sys.exit(1)
s = s.replace(old2, new2)

old3 = """                    loud = [f for f in ex if f["tag"] in ("extract:база", "extract:таблицы")]
                    if loud:
                        notify.send_lvl(2, "ИНЪЕКЦИЯ\\n%s\\n%s" % (host, loud[0]["extra"]))"""
new3 = """                    loud = [f for f in ex if f.get("tag") in ("extract:база", "extract:таблицы")]
                    if loud:
                        notify.send_lvl(2, "ИНЪЕКЦИЯ\\n%s\\n%s" % (host, loud[0].get("extra", "")))"""
if s.count(old3) != 1:
    print("инъекции: блок не найден"); sys.exit(1)
s = s.replace(old3, new3)

old4 = """def work(host, st, use_browser=True, full=False):
    rec = st.get(host) or {}
    if rec.get("done"):
        return host, rec
    try:
        return _work(host, st, use_browser, full)
    finally:
        http.drop(host)"""
new4 = """def work(host, st, use_browser=True, full=False):
    rec = st.get(host) or {}
    if rec.get("done"):
        return host, rec
    try:
        return _work(host, st, use_browser, full)
    except Exception:
        _log("%s сбой: %s" % (host, traceback.format_exc().replace("\\n", " | ")[:300]))
        rec = st.get(host) or {}
        rec.setdefault("notes", []).append("сбой")
        rec["done"] = True
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        st[host] = rec
        _DIRTY[0] = True
        return host, rec
    finally:
        http.drop(host)"""
if s.count(old4) != 1:
    print("work: не найден"); sys.exit(1)
s = s.replace(old4, new4)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
