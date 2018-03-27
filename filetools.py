import paths, platform, os, re
import movie as movie_tools
from datetime import datetime
import diskstation as ds
from shutil import copy2
from config import configuration_manager as cfg
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
_config = cfg()

# Try to determine creation date of folder
def get_creation_date(path_to_file_or_folder, convert=False):
    if platform.system() == 'Linux': # Not supported
        return None
    if platform.system() == 'Windows':
        ret_time = os.path.getctime(path_to_file_or_folder)
        ret_time.replace(microsecond=0)
        return ret_time if convert is False \
            else datetime.fromtimestamp(ret_time)

# Create nfo file with IMDb-id for movie
def create_nfo(full_path, imdb, type):
    if type == "movie":
        file_string = "movie.nfo"
    elif type == "tv":
        file_string = "tvshow.nfo"
    else:
        pr.error("wrong type for create_nfo: {}".format(type))
    nfo_path = os.path.join(full_path, file_string)
    if not os.path.isfile(nfo_path):
        try:
            with open(nfo_path, 'w') as newfile:
                newfile.write(imdb)
            return True
        except:
            pr.warning("could not create nfo: {}".format(full_path))
            return False
    else:
        pr.warning("nfo already exists: {}".format(full_path))
        return True

# Check if file is empty
def is_file_empty(full_path):
    try:
        if os.stat(full_path).st_size is 0:
            return True
    except:
        pr.warning("is_file_empty: could not check file {}".format(full_path))
        return False

# Copy file to dest, append  YYYY-MM-DD-HHMM
def backup_file(src_full_path, dest_dir_full_path):
    now = datetime.now().strftime("%Y-%m-%d-%H%M")
    dest = os.path.join(dest_dir_full_path, now)
    try:
        if not os.path.exists(dest):
            os.makedirs(dest)
        copy2(src_full_path, dest)
        return True
    except:
        pr.warning("backup_file: could not backup file: {}".format(src_full_path))
        pr.warning("backup_file: make sure to run scripts as sudo!")
        return False

# Copy databases to webserver file loc
def copy_dbs_to_webserver(tv_or_db):
    htdoc_loc = _config.get_setting("path", "webserver")
    db = None
    if tv_or_db == "tv":
        db = _config.get_setting("path", "tvdb")
    if tv_or_db == "movie":
        db = _config.get_setting("path", "movdb")
    if db:
        copy2(db, htdoc_loc)
        pr.info("copied  to webserver htdocs: {}".format(db));
    else:
        pr.warning("could not copy to htdocs!");

# Helper function to guess_folder_type
def _type_points(folder):
    folder = movie_tools.remove_extras_from_folder(folder)
    regex = {'season': '\.[Ss]\d{2}\.', 'episode': "\.[Ss]\d{2}[Ee]\d{2}",
             'movie': "\.\d{4}\.\d{3,4}p\."}
    points = {'season': 0, 'episode': 0, 'movie': 0}
    for key in regex:
        if _is_regex_match(regex[key], folder):
            points[key] += 1
    return points

# Helper function to guess_folder_type
def _is_regex_match(regex, string):
    rgx = re.compile(regex)
    match = re.search(rgx, string)
    if match:
        return True
    return False

# Try to determine if folder (as string) is a movie / season / episode
def guess_folder_type(folder):
    points = _type_points(folder)
    max_key = 0
    winner_key = None
    for key in points:
        if points[key] > max_key:
            max_key = points[key]
            winner_key = key
    return winner_key
