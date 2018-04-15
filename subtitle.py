# -*- coding: utf-8 -*-
import argparse, os, paths, user_input, shlex, subprocess, re
from printout import print_class as pr
import filetools as ftool
import tvshow as tvtool
import movie as mtool
import db_mov as movie_database
import subscene

mdb = movie_database.database()

class mkvinfo_command:
    def __init__(self, vid_file_path):
        self.file = vid_file_path
        self.o = self._run()
    def _run(self):
        pr.info(f"running command: [mkvinfo \"{self.file}\"]")
        args = ["mkvinfo", self.file]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out
    def get_o(self):
        return self.o
    output = property(get_o)

# extract tracks from mkv-file
def mkvextract(vid_file_path, track, lang):
    dest = vid_file_path.replace(".mkv", f".{lang}.srt")
    if not ftool.is_existing_file(dest):
        pr.info(f"mkvextract tracks {vid_file_path} {track}:{dest}")
        args = ["mkvextract", "tracks", vid_file_path, f"{track}:{dest}"]
        process = subprocess.Popen(args)
        out, err = process.communicate()
    else:
        pr.warning(f"[{dest}] already exists! skipping")

# load language words from txt-files
def _load_words(lang):
    ret_list = []
    script_loc = os.path.dirname(os.path.realpath(__file__))
    word_file = f"sub_words_{lang}.txt"
    word_file_path = os.path.join(script_loc, "txt", word_file)
    if not ftool.is_existing_file(word_file_path):
        pr.error(f"could not find file [{word_file_path}]")
        return None
    try:
        with open(word_file_path, 'r', encoding="ISO-8859-1") as words:
            for line in words:
                ret_list.append(line.replace("\n", ""))
    except:
        pr.error(f"could not load file [{word_file}]")
        return None
    return ret_list

def determine_lang(srt_file_path):
    words_en = _load_words("en")
    words_sv = _load_words("sv")
    points = { "en" : 0, "sv": 0 }
    with open(srt_file_path, 'r', encoding="ISO-8859-1") as srt_lines:
        for srt_line in srt_lines:
            for word in words_en:
                if word in srt_line:
                    points["en"] += 1
            for word in words_sv:
                if word in srt_line:
                    points["sv"] += 1
    if points["sv"] == points["en"]:
        return None
    if points["sv"] > points["en"]:
        return "sv"
    return "en"

def _vid_to_srt_filename(vid_file_name, lang):
    vid_types = [".mkv", ".avi", ".mp4"]
    for type in vid_types:
        if vid_file_name.endswith(type):
            return vid_file_name.replace(type, f".{lang}.srt")
    return None


# rename srt to match video file
def rename_srt(srt_file_path, lang):
    sub_dir = os.path.dirname(os.path.realpath(srt_file_path))
    sub_file_name = os.path.basename(srt_file_path)
    file_list = os.listdir(sub_dir)
    vid_files = [] # vid files in same dir as passed subtitle
    for vid in file_list:
        if vid.endswith(".mkv") or vid.endswith(".avi") or vid.endswith(".mp4"):
            srt_file_name = _vid_to_srt_filename(vid, lang)
            vid_files.append({ "file" : vid, "srt_name" : srt_file_name})
    sub_se = tvtool.guess_season_episode(sub_file_name)
    for vid in vid_files:
        if ftool.is_existing_file(vid['srt_name']):
            if vid['srt_name'] == sub_file_name:
                return
            continue #already has subtitle
        if tvtool.guess_season_episode(vid["file"]) == sub_se:
            pr.info(f"srt:         [{sub_file_name}]", brackets_color="yellow")
            dst_path = os.path.join(sub_dir, vid['srt_name'])
            try:
                os.rename(srt_file_path, dst_path)
                pr.info(f"renamed ==> [{vid['srt_name']}]", brackets_color="green")
                return
            except:
                pr.warning(f"could not rename [{sub_file_name}]")
            break
    pr.warning(f"could not rename/find match for [{sub_file_name}]")

# list subtitle tracks in mkv-file
def find_srt_tracks(vid_file_path):
    re_track_number = re.compile("track\\snumber:\\s\\d{1,2}", re.IGNORECASE)
    mkvinfo = mkvinfo_command(vid_file_path)
    lines = str(mkvinfo.output).split("\\n")
    tracks = {}
    track_number = -1
    for line in lines:
        match = re_track_number.search(line)
        if match:
            track_number = match[0].split(":")[1].replace(" ", "")
            tracks[int(track_number)] = { "type" : None, "lang" : None, "name" : None}
        if "Track type: subtitles" in line:
            tracks[int(track_number)]["type"] = "sub"
        if "Language: " in line:
            tracks[int(track_number)]["lang"] = line.split(": ")[1]
        if "Name: " in line:
            tracks[int(track_number)]["name"] = line.split(": ")[1]
    srt_tracks = []
    for track_no in tracks:
        lang = "unkown"
        if tracks[track_no]["type"]:
            if tracks[track_no]["name"]:
                if "nglish" in tracks[track_no]["name"]:
                    lang = "en"
                elif "wedish" in tracks[track_no]["name"]:
                    lang = "sv"
            if tracks[track_no]["lang"]:
                #TODO: Check that eng/swe is correct string for matching
                if "eng" in tracks[track_no]["lang"]:
                    lang = "en"
                elif "swe" in tracks[track_no]["lang"]:
                    lang = "sv"
        srt_tracks.append({"track" : track_no, "lang" : lang})
    return srt_tracks

def subscene_search(movie_title, movie_folder):
    pr.info(f"searching subscene for {movie_title}")
    folder_words = movie_folder.split(".")
    film = subscene.search(movie_title)
    sub_candidates = { "en" : [], "sv" : []}
    sv_winner = None
    en_winner = None # TODO: can hearing impaired be identified?
    for sub in film.subtitles:
        if sub.language.lower() == "swedish":
            sub_candidates["sv"].append({"name" : str(sub), "url": sub.zipped_url, "points" : 0})
        elif sub.language.lower() == "english":
            sub_candidates["en"].append({"name" : str(sub), "url": sub.zipped_url, "points" : 0})
    for sv_sub in sub_candidates["sv"]:
        for word in folder_words:
            if word in sv_sub["name"]:
                sv_sub["points"] += 1
    for en_sub in sub_candidates["en"]:
        for word in folder_words:
            if word in en_sub["name"]:
                en_sub["points"] += 1
    old_points = -1
    for sv_sub in sub_candidates["sv"]:
        if sv_sub["points"] > old_points:
            sv_winner = sv_sub
            old_points = sv_sub["points"]
    old_points = -1
    for en_sub in sub_candidates["en"]:
        if en_sub["points"] > old_points:
            en_winner = en_sub
            old_points = en_sub["points"]
    return { "sv" : sv_winner, "en": en_winner }

pr = pr(os.path.basename(__file__))
parser = argparse.ArgumentParser(description='subTools')
parser.add_argument('command', type=str, help='commands: ripall, renameall')
parser.add_argument('--movie', "-m", type=str, dest="movie_folder", default=None, help='movie folder')
args = parser.parse_args()
cwd = os.getcwd() # get working directory

if args.command == "ripall":
    pr.info(f"extracting all srts from mkv-files in dir [{cwd}]")
    files = os.listdir(cwd)
    files.sort()
    for file in files:
        if file.endswith(".mkv"):
            vid = os.path.join(cwd, file)
            srts = find_srt_tracks(vid)
            for srt in srts:
                #TODO: Extract unknown lang and determine if eng/swe
                if srt["lang"] == "sv" or srt["lang"] == "en":
                    mkvextract(vid, srt["track"] - 1, srt["lang"])
elif args.command == "renameall": # FIXME: do for movies
    files = os.listdir(cwd)
    files.sort()
    for file in files:
        if file.endswith(".srt"):
            lang = determine_lang(os.path.join(cwd, file))
            if not lang:
                pr.warning(f"could not determine lang of [{file}]")
                continue
            rename_srt(os.path.join(cwd, file), lang)
elif args.command == "search":
    if not args.movie_folder:
        pr.error("pass movie folder with --movie / -m")
    elif mdb.exists(args.movie_folder.replace(r"/", "")):
        title = mdb.omdb_data(args.movie_folder, "Title")
        if title:
            subs = subscene_search(title, args.movie_folder.replace(r"/", ""))
        else:
            subs = subscene_search(mtool.determine_title(args.movie_folder), args.movie_folder.replace(r"/", ""))
        #TODO: dl subs, extract, determine lang, rename, delete zips
        print(subs["en"]["url"])
        print(subs["sv"]["url"])
    else:
        pr.warning(f"{args.movie_folder} not in db")
