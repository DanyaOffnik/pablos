import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import vuln


def main():
    ap = argparse.ArgumentParser(prog="vuln.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    r = sub.add_parser("run")
    r.add_argument("--cve", required=True)
    r.add_argument("--source", required=True, help="run | file:<path> | list:h1,h2")
    r.add_argument("--threads", type=int, default=8)
    r.add_argument("--timeout", type=int, default=30)
    r.add_argument("--limit", type=int, default=0)

    rp = sub.add_parser("report")
    rp.add_argument("--cve", required=True)

    g = sub.add_parser("grab")
    g.add_argument("--cve", required=True)

    a = ap.parse_args()

    if a.cmd == "list":
        rows = vuln.catalog()
        if not rows:
            print("база пуста")
        for cid, title, plug in rows:
            print("%-18s %-28s %s" % (cid, plug, title))
        return

    if a.cmd == "report":
        p = vuln.report(a.cve)
        print(p or "нечего включать в отчёт")
        return

    if a.cmd == "grab":
        rows = vuln.grab(a.cve)
        print("\n".join(x["host"] + "\t" + x.get("shell", "") for x in rows) or "ничего не взято")
        return

    src = a.source
    if src == "run":
        hosts = vuln.sources_run()
    elif src.startswith("file:"):
        hosts = vuln.sources_file(src[5:])
    elif src.startswith("list:"):
        hosts = [h.strip() for h in src[5:].split(",") if h.strip()]
    else:
        raise SystemExit("bad source")
    print("целей: %d" % len(hosts))
    vuln.run(a.cve, hosts, a.threads, a.timeout, a.limit)


if __name__ == "__main__":
    main()