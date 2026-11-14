src = open("night.py", encoding="utf-8").read()
src = src.replace("consec = total = 0\nt0 = time.time()",
                  "consec = total = 0\nspeed = 2.4\nt0 = time.time()")
src = src.replace('for phase, cap in [("targets.txt", 0),',
                  'for phase, cap in [("tier0.txt", 0), ("targets.txt", 0),')
src = src.replace('cool(30 if consec < 3 else 240, "ошибок %d" % consec)',
                  'speed = min(3.0, speed * 1.5)\n                    cool(30 if consec < 3 else 240, "ошибок %d" % consec)')
src = src.replace("time.sleep(random.uniform(0.8, 1.8))",
                  "speed = max(0.9, speed - 0.03)\n                time.sleep(speed + random.uniform(0, 0.5))")
src = src.replace('print("  %d попыток, %.1f мин, %.2f с/шт" % (total, el / 60, el / total), flush=True)',
                  'print("  %d попыток, %.1f мин, %.2f с/шт, темп %.2f" % (total, el / 60, el / total, speed), flush=True)')
open("night.py", "w", encoding="utf-8").write(src)
print("патч применён")
