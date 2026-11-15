import sys, time
sys.path.insert(0, r"C:\work\hunt2")
from core import http
for h in ("nonexistent-abc123xyz.md", "10.255.255.1"):
    t = time.time()
    try:
        http.get(h, "/", tries=1)
        print(h, "ok", round(time.time() - t, 1))
    except Exception as e:
        print(h, type(e).__name__, round(time.time() - t, 1))
