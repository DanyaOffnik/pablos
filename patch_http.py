import io
c = r"C:\work\hunt2\core\config.py"
h = r"C:\work\hunt2\core\http.py"

s = io.open(c, encoding="utf-8-sig").read()
if "CONNECT" not in s:
    s = s.replace("TIMEOUT = 20", "TIMEOUT = 20\nCONNECT = 8", 1)
    io.open(c, "w", encoding="utf-8-sig", newline="\n").write(s)
    print("config: CONNECT добавлен")

s = io.open(h, encoding="utf-8-sig").read()
orig = s
s = s.replace("RETRIES = 2", "RETRIES = 1", 1)
s = s.replace("RETRIES = 1\n",
              "RETRIES = 1\n\n\ndef _tmo():\n    return (config.CONNECT, config.TIMEOUT)\n", 1)
s = s.replace("timeout=config.TIMEOUT,", "timeout=_tmo(),", 1)
s = s.replace('"timeout": timeout or config.TIMEOUT}',
              '"timeout": timeout or _tmo()}', 1)
if s == orig:
    print("http: НЕ ИЗМЕНЕНО")
else:
    io.open(h, "w", encoding="utf-8-sig", newline="\n").write(s)
    print("http: патч накатан")
