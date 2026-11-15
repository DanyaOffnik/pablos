"""Build a version hash table for a descriptor.

Downloads every released version inside the affected range from
downloads.wordpress.org, hashes the oracle asset and writes hashes.json.
"""
import argparse
import hashlib
import io
import json
import os
import sys
import zipfile
import urllib.request

API = "https://api.wordpress.org/plugins/info/1.0/%s.json"
DL = "https://downloads.wordpress.org/plugin/%s.%s.zip"
MAX_ASSET = 3 * 1024 * 1024


def vparse(s):
    return tuple(int(x) for x in __import__("re").findall(r"\d+", s or "")) or (0,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cve", required=True)
    ap.add_argument("--asset", required=True, help="path inside the plugin zip")
    ap.add_argument("--db", default=os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "data", "vuln"))
    a = ap.parse_args()

    d = os.path.join(a.db, a.cve)
    with open(os.path.join(d, "vuln.json"), encoding="utf-8") as f:
        v = json.load(f)

    slug = v["plugin"]
    bound = v.get("affected", {}).get("version", "999")
    info = json.load(urllib.request.urlopen(API % slug, timeout=30))
    versions = list(info.get("versions", {}).keys())
    versions = [x for x in versions if x not in ("trunk", "beta", "nightly")]
    versions = [x for x in versions if vparse(x) <= vparse(bound)]
    if not versions:
        print("нет версий в диапазоне")
        return

    out = {}
    for ver in versions:
        try:
            raw = urllib.request.urlopen(DL % (slug, ver), timeout=60).read()
            z = zipfile.ZipFile(io.BytesIO(raw))
            name = [n for n in z.namelist() if n.endswith(a.asset)]
            if not name:
                print("%-8s нет ассета" % ver)
                continue
            data = z.read(name[0])
            if len(data) > MAX_ASSET:
                print("%-8s слишком большой" % ver)
                continue
            out[hashlib.sha1(data).hexdigest()] = ver
            print("%-8s ok" % ver)
        except Exception as e:
            print("%-8s %s" % (ver, type(e).__name__))

    with open(os.path.join(d, "hashes.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("хешей: %d -> %s" % (len(out), os.path.join(d, "hashes.json")))


if __name__ == "__main__":
    sys.exit(main())