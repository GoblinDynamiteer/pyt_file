import sys, os

import configparser
config = configparser.ConfigParser()

def get_path_of_script_file(script__file__):
    return os.path.dirname(os.path.realpath(__file__))

def get_path_to_file_same_dir(script__file__, filename):
    return os.path.join(get_path_of_script_file(script__file__), filename)

setting_location = get_path_to_file_same_dir(__file__, "settings.ini")

config.read(setting_location)

for mod_path in config['modpath']:
    sys.path.append(config['modpath'][mod_path])
