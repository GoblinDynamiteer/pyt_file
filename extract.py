# -*- coding: utf-8 -*-
import argparse, os, paths, user_input, re, shutil
import movie, filetools, tvshow
from config import configuration_manager as cfg
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
_config = cfg()
script = os.path.basename(__file__)

def check_valid_source_folder(source_path):
    if not os.path.exists(source_path): # Input folder is not a real dir
        pr.error("[ {} ] does not exist, quitting!".format(source_path))
        exit()

# Move movie file
def move_mov(file):
    source_path = os.path.join(cwd, file)
    folder = file.replace(".mkv", "")
    check_valid_source_folder(source_path)  # Will exit script if not valid
    dest_path = os.path.join(movie.root_path(),
        movie.determine_letter(file), folder)
    if user_input.yes_no("Move to: [ {} ]".format(dest_path),
        script_name=os.path.basename(__file__)):
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        # TODO: Use subprocess.call instead of os.system
        os.system("mv {} {}".format(source_path, dest_path))
        pr.info("File moved!")

# Move episode
def move_ep(file_name_s):
    src = os.path.join(cwd, file_name_s)
    dest = tvshow.create_new_show_from_ep(file_name_s)
    pr.info(f'move [{file_name_s}]')
    pr.info(f'---> [{dest}]')
    if user_input.yes_no("Proceed with move?", script_name=None):
        # TODO: Use subprocess.call instead of os.system
        os.system("mv {} \"{}\"".format(src, dest))
        pr.info("File moved!")

# Move episode
def extract_ep(folder):
    src = os.path.join(cwd, folder)
    dest = tvshow.create_new_show_from_ep(folder)
    rar_file = None
    for f in os.listdir(src):
        if f.endswith(".rar"):
            rar_file = str(f)
    if rar_file is None:
        pr.warning(f"could not find .rar in [{folder}]")
        quit()
    src_rar = os.path.join(src, rar_file)
    pr.info(f"found rar-file: [{rar_file}]")
    pr.info(f'extract [{folder}]')
    pr.info(f'------> [{dest}]')
    if user_input.yes_no("proceed with extraction?", script_name=None):
        # TODO: Use subprocess.call instead of os.system
        os.system("unrar e \"{}\" \"{}\"".format(src_rar, dest))
        pr.info("done!")

# Find rar and nfo-files passed in directory
def extract_mov(folder):
    source_path = os.path.join(cwd, folder)
    check_valid_source_folder(source_path)  # Will exit script if not valid
    dest_path = os.path.join(movie.root_path(), movie.determine_letter(folder), folder)
    rar_file = None
    nfo_file = None
    for f in os.listdir(source_path):
        if f.endswith(".rar"):
            rar_file = str(f)
        if f.endswith(".nfo"):
            nfo_file = str(f)
    # TODO: Check != sub rar
    if rar_file is None:
        pr.warning(f"could not find .rar in [{folder}]")
        quit()
    source_file = os.path.join(source_path, rar_file)
    pr.info("Found rar-file: [ {} ]".format(os.path.basename(source_file)))
    if user_input.yes_no("Extract to: [ {} ]".format(dest_path),
        script_name=os.path.basename(__file__)):
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
                    pr.info("Found IMDb-id in nfo-file: [ {} ]".format(imdb_id))
                    filetools.create_nfo(dest_path, "http://www.imdb.com/title/{}"
                        .format(imdb_id), "movie")

def extract_season(folder):
    source_path = os.path.join(cwd, folder)
    check_valid_source_folder(source_path) # Will exit script if not valid
    dest_path = os.path.join(tvshow.root_path(), tvshow.guess_ds_folder(folder))
    if os.path.exists(dest_path):
        pr.info("[ {} ] exists!".format(dest_path))
    season = tvshow.guess_season(folder)
    pr.info("guessed season: {}".format(season))
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
        pr.info("Creating {}".format(dest_path))
        os.makedirs(dest_path)
    for root, dirs, files in os.walk(full_source_path):
        for file in files:
            if file.endswith(".subs.rar") or file.endswith(".subs.sfv"):
                if not found_subs:
                    found_subs = True
                    pr.info("Found subtitles - will move before extract")
                file_to_move = os.path.join(root, file)
                pr.info("Moving {} to subs storage".format(file))
                shutil.move(file_to_move, dest_path)

parser = argparse.ArgumentParser(description='TV/Movie UnRarer')
parser.add_argument('dir', type=str, help='Path to movie or tv source')
args = parser.parse_args()

dir_name = movie.remove_extras_from_folder(args.dir)
cwd = os.getcwd() # Get working directory
guessed_type = filetools.guess_folder_type(dir_name)

if guessed_type == 'movie':
    pr.info("Guessed movie!")
    if(args.dir.endswith(".mkv")):
        pr.info("is file (mkv)")
        move_mov(args.dir)
    else:
        extract_mov(args.dir)
elif guessed_type == 'episode':
    pr.info("Guessed tv episode!")
    if(args.dir.endswith(".mkv")):
        pr.info("is file (mkv)")
        move_ep(args.dir)
    else:
        extract_ep(args.dir)
elif guessed_type == 'season':
    pr.info("Guessed tv season!")
    extract_season(args.dir)
else:
    pr.error("Could not determine type of [ {} ]".format(dir_name))
    quit()
