import sys, os

import configparser
config = configparser.ConfigParser()
config.read('settings.ini')

for mod_path in config['modpath']:
    sys.path.append(config['modpath'][mod_path])
