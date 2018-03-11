# Handle settings in settings.ini

import paths
import configparser, os
from printout import print_warning

class configuration_manager:
    def __init__(self):
        self.config = None;
        self.filename = paths.get_path_to_file_same_dir(__file__, "settings.ini")
        self.load_success = False
        self._load_settings()

    def _load_settings(self):
        if os.path.isfile(self.filename):
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.filename)
                self.load_success = True
            except:
                print_warning("configuration_manager: Could not load {}".
                    format(self.filename))
        else:
            print_warning("configuration_manager: file missing: {}".
                format(self.filename))

    def get_setting(self, section, key):
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        else:
            print_warning("configuration_manager: {}:{} does not exist in {}".
                format(section, key, self.filename))
            return None
