import sys, time
sys.path.insert(0, r"C:\work\hunt2")
from modules import night

t = time.time()
print("1) зомби:", night._call(time.sleep, 2, 10)[2], round(time.time() - t, 1), "с (ждём ~2)")

t = time.time()
print("2) норма:", repr(night._call(time.sleep, 5, 1)[2]), round(time.time() - t, 1), "с (ждём ~1)")

t = time.time()
for _ in range(20):
    night._call(time.sleep, 1, 30)
print("3) 20 зомби:", round(time.time() - t, 1), "с (ждём ~2, а не 20)")
