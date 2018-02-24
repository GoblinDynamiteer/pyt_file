import sys, os

home = os.getenv("HOME")

for mod_path in ["pyt_db" , "pyt_input"]:
    p = os.path.join(home, "code", mod_path)
    sys.path.append(p)
