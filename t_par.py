import sys, time, threading
sys.path.insert(0, r"C:\work\hunt2")
from modules import night

def w():
    night._call(time.sleep, 1, 30)

ths = [threading.Thread(target=w) for _ in range(40)]
t = time.time()
for x in ths: x.start()
for x in ths: x.join()
print("40 зомби в 40 потоках:", round(time.time() - t, 1), "с (ждём ~3, а не 40)")
