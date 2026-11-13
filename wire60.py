# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\core\http.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """    last = None
    for attempt in range((RETRIES if tries is None else tries) + 1):"""
new = """    last = None
    last_r = None
    for attempt in range((RETRIES if tries is None else tries) + 1):"""
if s.count(old) != 1:
    print("http: цикл не найден"); sys.exit(1)
s = s.replace(old, new)

old2 = """        if r.status_code in (429, 503) and attempt < RETRIES:
            time.sleep(1.2 * (attempt + 1))
            continue
        return r
    if last is not None:
        raise last
    raise RuntimeError("request failed")"""
new2 = """        last_r = r
        if r.status_code in (429, 503) and attempt < RETRIES:
            time.sleep(1.2 * (attempt + 1))
            continue
        return r
    if last_r is not None:
        return last_r
    if last is not None:
        raise last
    raise RuntimeError("request failed")"""
if s.count(old2) != 1:
    print("http: хвост не найден"); sys.exit(1)
s = s.replace(old2, new2)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
