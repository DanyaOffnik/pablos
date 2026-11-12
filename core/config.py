import os
import sys

if getattr(sys, "frozen", False):
    BASE = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA = os.path.join(BASE, "data")
TPL = os.path.join(BASE, "templates")
PROF = os.path.join(BASE, "profiles")
DICT = os.path.join(DATA, "dict")
PROFILES = PROF
SESS = os.path.join(DATA, "sessions")
LOGS = os.path.join(DATA, "logs")
BROWSER = os.path.join(DATA, "browser")
STATE = os.path.join(DATA, "state")
LEASE = os.path.join(DATA, "lease")
RUNS = os.path.join(DATA, "runs")
REPORTS = os.path.join(DATA, "reports")
DOSSIER = os.path.join(DATA, "dossier")

for _d in (DATA, DICT, PROFILES, TPL, SESS, LOGS, BROWSER, STATE, LEASE, RUNS, REPORTS, DOSSIER):
    os.makedirs(_d, exist_ok=True)

LIST = os.path.join(DATA, "list.txt")
DONE = os.path.join(DATA, "done.txt")
TRASH = os.path.join(DATA, "trash.txt")
STOP = os.path.join(DATA, "STOP")

PROXIES = os.path.join(DATA, "proxies.txt")

TIMEOUT = 20

LEASE_TTL = 1800
HEARTBEAT = 900
