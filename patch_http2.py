import io
h = r"C:\work\hunt2\core\http.py"
s = io.open(h, encoding="utf-8-sig").read()
orig = s
old = '''        except Exception as e:
            last = e
            msg = str(e)
'''
new = '''        except Exception as e:
            last = e
            msg = str(e)
            if "Timeout" in type(e).__name__ or "timed out" in msg.lower():
                drop(host)
                break
'''
s = s.replace(old, new, 1)
if s == orig:
    print("НЕ ИЗМЕНЕНО")
else:
    io.open(h, "w", encoding="utf-8-sig", newline="\n").write(s)
    print("патч накатан")
