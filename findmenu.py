import glob
for p in glob.glob("**/*.py", recursive=True):
    try:
        L = open(p, encoding="utf-8", errors="ignore").read().splitlines()
    except Exception:
        continue
    for i, l in enumerate(L):
        if "возобновить" in l:
            print("=" * 20, p, "строка", i + 1)
            print("\n".join(L[max(0, i - 25):i + 15]))
            print()