# -*- coding: utf-8 -*-

import argparse, os, paths, user_input, re
import movie, filetools

parser = argparse.ArgumentParser(description='TV/Movie UnRarer')
parser.add_argument('dir', type=str, help='Path to movie or tv source')
args = parser.parse_args()

dir_name = args.dir
cwd = os.getcwd() # Get working directory
dest_path = os.path.join(movie.root_path(), movie.determine_letter(dir_name), dir_name)
source_path = os.path.join(cwd, dir_name)

rar_file = None
nfo_file = None

# Find rar and nfo-files passed in directory
for f in os.listdir(source_path):
    if f.endswith(".rar"):
        rar_file = str(f)
    if f.endswith(".nfo"):
        nfo_file = str(f)

# TODO: Check != sub rar
if rar_file is None:
    print("Could not find .rar in {}". format(dir_name))
    quit()

source_file = os.path.join(source_path, rar_file)
if user_input.yes_no("EXTRACT:\n{} \n --> \n{}".format(source_file, dest_path)):
    # TODO: Use subprocess.call instead of os.system
    os.system("unrar e \"{}\" \"{}\"".format(source_file, dest_path))

else:
    quit()

if nfo_file is not None:
    pattern = re.compile("tt\d{2,}")
    nfo_file = os.path.join(source_path, nfo_file)
    with open(nfo_file, 'r', encoding='utf-8', errors='ignore') as nfo:
        for line in nfo:
            match = re.search(pattern, line)
            if match:
                imdb_id = match[0]
                print("Found IMDb-id in nfo-file: {0}".format(imdb_id))
                filetools.create_nfo(dest_path, "http://www.imdb.com/title/{}".format(imdb_id))

# TODO: Determinge tv/movie -- now: assume Movie
