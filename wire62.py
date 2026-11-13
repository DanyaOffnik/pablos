# -*- coding: utf-8 -*-
import io, py_compile, sys
P = r"C:\work\hunt2\core\http.py"
s = io.open(P, encoding="utf-8-sig").read()

old = """    s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT, verify=False)"""
new = """    s = creq.Session(impersonate="chrome", timeout=config.TIMEOUT, verify=False,
                     http2=False)"""
if s.count(old) != 1:
    print("http: сессия не найдена"); sys.exit(1)
s = s.replace(old, new)

old2 = """        except Exception as e:
            last = e
            if not sess:
                px = _PROX.get(host)
                if px:
                    _bad(px)
                drop(host)"""
new2 = """        except Exception as e:
            last = e
            msg = str(e)
            if "HTTP/2" in msg or "stream" in msg or "reset by server" in msg:
                drop(host)
                time.sleep(0.4)
                continue
            if not sess:
                px = _PROX.get(host)
                if px:
                    _bad(px)
                drop(host)"""
if s.count(old2) != 1:
    print("http: обработчик не найден"); sys.exit(1)
s = s.replace(old2, new2)

io.open(P, "w", encoding="utf-8-sig", newline="\n").write(s)
py_compile.compile(P, doraise=True)
print("ок")
