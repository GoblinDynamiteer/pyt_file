# -*- coding: utf-8 -*-

import argparse, os, paths, user_input
#in PYTHONPATH
import movie

parser = argparse.ArgumentParser(description='TV/Movie UnRarer')
parser.add_argument('dir', type=str, help='Path to movie or tv source')
args = parser.parse_args()

dir_name = args.dir
cwd = os.getcwd() # Get working directory
dest_path = os.path.join(movie.root_path(), movie.determine_letter(dir_name), dir_name)
source_path = os.path.join(cwd, dir_name)

rar_file = None
for f in os.listdir(source_path):
    if f.endswith(".rar"):
        rar_file = str(f)

source_file = os.path.join(source_path, rar_file)

# TODO: Check != sub rar
if rar_file is None:
    print("Could not find .rar in {}". format(dir_name))

if user_input.yes_no("EXTRACT:\n{} \n --> \n{}".format(source_file, dest_path)):
    os.system("unrar e \"{}\" \"{}\"".format(source_file, dest_path))

# TODO: Determinge tv/movie -- now: assume Movie
