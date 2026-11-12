# -*- coding: utf-8 -*-
import io, py_compile, sys

P = r"C:\work\hunt2\modules\report.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """def _sources(d):"""
new = """def _col(head, *names):
    for n in names:
        if n in head:
            return head.index(n)
    return -1


def _sources(d):"""
if s.count(old) != 1:
    print("report: _sources не найдено"); sys.exit(1)
s = s.replace(old, new)

old2 = """    for path in sources:
        head, rows = _read_csv(path)
        if "url" in head:
            i_h, i_t, i_u = head.index("хост"), head.index("метка"), head.index("url")
            i_c = head.index("код") if "код" in head else -1
            i_s = head.index("размер") if "размер" in head else -1
            for row in rows:
                h = row[i_h].strip().lower()
                e = hosts.setdefault(h, {"score": 0, "creds": "", "notes": [], "urls": []})
                e["urls"].append({"tag": row[i_t], "url": row[i_u],
                                  "code": row[i_c] if i_c >= 0 else "",
                                  "size": row[i_s] if i_s >= 0 else ""})
                e["notes"].append(row[i_t])
        elif "находки" in head:
            i_h = head.index("хост")
            i_sc = head.index("баллы") if "баллы" in head else -1
            i_n = head.index("находки") if "находки" in head else -1
            i_cr = head.index("вход") if "вход" in head else -1
            for row in rows:
                h = row[i_h].strip().lower()
                e = hosts.setdefault(h, {"score": 0, "creds": "", "notes": [], "urls": []})
                if i_sc >= 0:
                    try:
                        e["score"] = max(e["score"], int(row[i_sc]))
                    except Exception:
                        pass
                if i_n >= 0 and row[i_n].strip():
                    e["notes"] += [x.strip() for x in row[i_n].split(",") if x.strip()]
                if i_cr >= 0 and row[i_cr].strip():
                    e["creds"] = row[i_cr].strip()"""

new2 = """    for path in sources:
        head, rows = _read_csv(path)
        i_h = _col(head, "хост", "host")
        if i_h < 0:
            continue
        i_t = _col(head, "метка", "tag")
        i_u = _col(head, "url")
        i_c = _col(head, "код", "status")
        i_s = _col(head, "размер", "size")
        i_sc = _col(head, "баллы", "score")
        i_n = _col(head, "находки", "notes")
        i_cr = _col(head, "вход", "creds")
        for row in rows:
            if i_h >= len(row):
                continue
            h = row[i_h].strip().lower()
            if not h:
                continue
            e = hosts.setdefault(h, {"score": 0, "creds": "", "notes": [], "urls": []})
            if i_u >= 0 and i_u < len(row) and row[i_u].strip():
                e["urls"].append({"tag": row[i_t] if 0 <= i_t < len(row) else "",
                                  "url": row[i_u],
                                  "code": row[i_c] if 0 <= i_c < len(row) else "",
                                  "size": row[i_s] if 0 <= i_s < len(row) else ""})
            if i_t >= 0 and i_t < len(row) and row[i_t].strip():
                e["notes"].append(row[i_t])
            if i_sc >= 0 and i_sc < len(row):
                try:
                    e["score"] = max(e["score"], int(row[i_sc]))
                except Exception:
                    pass
            if i_n >= 0 and i_n < len(row) and row[i_n].strip():
                e["notes"] += [x.strip() for x in row[i_n].split(",") if x.strip()]
            if i_cr >= 0 and i_cr < len(row) and row[i_cr].strip():
                e["creds"] = row[i_cr].strip()"""
if s.count(old2) != 1:
    print("report: тело не найдено"); sys.exit(1)
s = s.replace(old2, new2)

old3 = """    st = _state(d)"""
new3 = """    st = _state(d) if isinstance(_state(d), dict) else {}"""
if s.count(old3) != 1:
    print("report: state не найдено"); sys.exit(1)
s = s.replace(old3, new3)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("report ок")
