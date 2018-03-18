# -*- coding: utf-8 -*-

import argparse, os, paths, user_input, re, shutil
import movie, filetools, tvshow
from printout import print_script_name as psn
from printout import print_color_between as pcb
from config import configuration_manager as cfg

_config = cfg()

def print_log(string):
    script = os.path.basename(__file__)
    if string.find('[') >= 0 and string.find(']') > 0:
        psn(script, "", endl=False)
        pcb(string, "blue")
    else:
        psn(script, string)

def check_valid_source_folder(source_path):
    script = os.path.basename(__file__)
    if not os.path.exists(source_path): # Input folder is not a real dir
        print_log("[ {} ] does not exist, quitting!".format(source_path))
        exit()

# Find rar and nfo-files passed in directory
def extract_mov(folder):
    source_path = os.path.join(cwd, dir_name)
    check_valid_source_folder(source_path)  # Will exit script if not valid
    dest_path = os.path.join(movie.root_path(), movie.determine_letter(dir_name), dir_name)
    rar_file = None
    nfo_file = None
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
    print_log("Found rar-file: [ {} ]".format(os.path.basename(source_file)))
    if user_input.yes_no("Extract to: [ {} ]".format(dest_path), script_name = script):
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
                    print_log("Found IMDb-id in nfo-file: [ {} ]".format(imdb_id))
                    filetools.create_nfo(dest_path, "http://www.imdb.com/title/{}".format(imdb_id))

def extract_season(folder):
    source_path = os.path.join(cwd, dir_name)
    check_valid_source_folder(source_path) # Will exit script if not valid
    dest_path = os.path.join(tvshow.root_path(), tvshow.guess_ds_folder(folder))
    if os.path.exists(dest_path):
        print_log("[ {} ] exists!".format(dest_path))
    season = tvshow.guess_season(folder)
    print_log("guessed season: {}".format(season))
    dest_path = os.path.join(dest_path, season)
    if user_input.yes_no("Extract to: {}".format(dest_path), script_name = script):
        move_subs(source_path, folder)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        # TODO: Use subprocess.call instead of os.system
        print("unrar e -r \"{}*.rar\" \"{}\"".format(source_path, dest_path))
        os.system("unrar e -r \"{}*.rar\" \"{}\"".format(source_path, dest_path))

def move_subs(full_source_path, folder):
    misc_root = _config.get_setting("path", "misc")
    dest_path = os.path.join(misc_root, "Subtitles", folder)
    found_subs = False
    if not os.path.exists(dest_path):
        print_log("Creating {}".format(dest_path))
        os.makedirs(dest_path)
    for root, dirs, files in os.walk(full_source_path):
        for file in files:
            if file.endswith(".subs.rar") or file.endswith(".subs.sfv"):
                if not found_subs:
                    found_subs = True
                    print_log("Found subtitles - will move before extract")
                file_to_move = os.path.join(root, file)
                print_log("Moving {} to subs storage".format(file))
                shutil.move(file_to_move, dest_path)

parser = argparse.ArgumentParser(description='TV/Movie UnRarer')
parser.add_argument('dir', type=str, help='Path to movie or tv source')
args = parser.parse_args()

dir_name = args.dir
cwd = os.getcwd() # Get working directory
guessed_type = filetools.guess_folder_type(dir_name)

if guessed_type == 'movie':
    print_log("Guessed movie!")
    extract_mov(dir_name)
elif guessed_type == 'episode':
    print_log("Guessed tv episode!")
elif guessed_type == 'season':
    print_log("Guessed tv season!")
    extract_season(dir_name)
else:
    print_log("Could not determine type of [ {} ]".format(dir_name))
    quit()
