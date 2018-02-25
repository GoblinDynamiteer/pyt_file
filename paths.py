import sys, os

home = os.getenv("HOME")

for mod_path in ["db" ,"io", "omdb-search", "file"]:
    p = os.path.join(home, "code", mod_path)
    sys.path.append(p)
