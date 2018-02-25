import platform
import os
from datetime import datetime

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
    if not os.path.isfile(full_path):
        with open(full_path + "movie.nfo", 'w') as newfile:
            newfile.write(imdb)

def is_file_empty(full_path):
    try:
        if os.stat(full_path).st_size is 0:
            return True
    except:
        print("is_file_empty: could not check file {}".format(full_path))
        return False
