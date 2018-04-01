# -*- coding: utf-8 -*-
import os, paths, argparse, re
from user_input import get_string as inp
from user_input import yes_no
from printout import print_class as pr
from datetime import datetime
from config import configuration_manager as cfg
import db_mov as movie_database

script_name = os.path.basename(__file__)
pr = pr(script_name)

class _file:
    def __init__(self, old_file, path, new_name):
        self.old_file = old_file
        self.new_name = new_name
        self.path = path

    def show_rename_operation(self):
        full_path = os.path.join(self.path, self.old_file)
        pr.info("{} --> {}".format(full_path, self.new_name))

    def rename(self):
        full_path = os.path.join(self.path, self.old_file)
        os.rename(full_path, self.new_name)

def guess_season_episode(string):
    rgx = re.compile('[Ss]\d{2}[Ee]\d{2}')
    match = re.search(rgx, string)
    if match:
        return match[0]
    return None

def sub_renamer(subs_path):
    sub_list = []
    for f in os.listdir(subs_path):
        if f.endswith(".srt"):
            sub_list.append(f)
    sub_list.sort()
    vid_path = inp("enter path to video file(s)", script_name)
    vid_path = os.path.expanduser(vid_path)
    if not os.path.exists(vid_path):
        pr.error("not a valid path: {}".format(vid_path))
        return
    vid_list = []
    for f in os.listdir(vid_path):
        if not f.endswith(".srt"):
            vid_list.append(f)
    vid_list.sort()
    _file_renames = []
    for vid in vid_list:
        se_vid = guess_season_episode(vid)
        for sub in sub_list:
            se_sub = guess_season_episode(sub)
            if se_sub.lower() == se_vid.lower():
                new_name = "{}.{}.srt".format(vid[:-4], "sv") #assume sv for now
                _file_renames.append(_file(sub, subs_path, new_name))
    pr.info("will rename subs:")
    for _file_rename in _file_renames:
        _file_rename.show_rename_operation()
    if yes_no("rename files?", script_name=script_name):
        for _file_rename in _file_renames:
            _file_rename.rename()
    else:
        pr.info("canceling...")

config = cfg()
parser = argparse.ArgumentParser(description='renamer')
parser.add_argument('func', type=str, help='renamer command:'
    'subs, sr (search and replace)')
args = parser.parse_args()

cwd = os.getcwd() # Get working directory

if(args.func == "subs"):
    sub_renamer(cwd)
else:
    pr.error("Wrong command: [ {} ]".format(args.func))
