import io
p = r"C:\work\hunt2\modules\night.py"
s = io.open(p, encoding="utf-8-sig").read()
s = s.replace("SLOTS = threading.BoundedSemaphore(16)\nSLOTS = threading.BoundedSemaphore(16)\n",
              "SLOTS = threading.BoundedSemaphore(16)\n")
s = s.replace("    _TL.deadline = time.time() + 600\n    _TL.deadline = time.time() + 600\n",
              "    _TL.deadline = time.time() + 600\n")
s = s.replace("_PAINT = [False]\n\n\n_PAINT = [False]\n", "_PAINT = [False]\n")
io.open(p, "w", encoding="utf-8-sig", newline="\n").write(s)
print("dedup ok")
