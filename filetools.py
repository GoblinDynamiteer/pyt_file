import platform, os, re
from datetime import datetime
import diskstation as ds
from printout import print_warning
from shutil import copy2

# Try to determine creation date of folder
def get_creation_date(path_to_file_or_folder, convert=False):
    if platform.system() == 'Linux': # Not supported
        return None
    if platform.system() == 'Windows':
        ret_time = os.path.getctime(path_to_file_or_folder)
        ret_time.replace(microsecond=0)
        return ret_time if convert is False else datetime.fromtimestamp(ret_time)

# Create nfo file with IMDb-id for movie
def create_nfo(full_path, imdb):
    nfo_path = os.path.join(full_path, "movie.nfo")
    if not os.path.isfile(nfo_path):
        try:
            with open(nfo_path, 'w') as newfile:
                newfile.write(imdb)
            return True
        except:
            print_warning("create_nfo: Could not create movie.nfo: {}".format(full_path))
            return False
    else:
        print_warning("create_nfo: movie.nfo already exists: {}".format(full_path))
        return True

def is_file_empty(full_path):
    try:
        if os.stat(full_path).st_size is 0:
            return True
    except:
        print_warning("is_file_empty: could not check file {}".format(full_path))
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
        print_warning("backup_file: Could not backup file: {}".format(src_full_path))
        print("Make sure to run scripts as sudo!")
        return False

def _type_points(folder):
    regex = {'season': '\.[Ss]\d{2}\.', 'episode': "\.[Ss]\d{2}[Ee]\d{2}",
             'movie': "\.\d{4}\.\d{3,4}p\."}
    points = {'season': 0, 'episode': 0, 'movie': 0}
    for key in regex:
        if _is_regex_match(regex[key], folder):
            points[key] += 1
    return points

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
