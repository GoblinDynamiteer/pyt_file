# Handle settings in settings.ini
import paths
import configparser, os
from printout import print_blue, print_no_line, print_color_between
from printout import print_script_name as psn
from printout import print_color_between as pcb
from printout import print_error, print_warning

def print_log(string, category=None):
    script = os.path.basename(__file__)
    psn(script, "", endl=False) # Print script name
    if category == "error":
        print_error("Error: ", endl=False)
    if category == "warning":
        print_warning("Warning: ", endl=False)
    if string.find('[') >= 0 and string.find(']') > 0:
        pcb(string, "blue")
    else:
        print(string)

class configuration_manager:
    def __init__(self):
        self.config = None;
        self.filename = paths.get_path_to_file_same_dir(__file__,
            "settings.ini")
        self.load_success = False
        self._load_settings()

    def _load_settings(self):
        if os.path.isfile(self.filename):
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.filename)
                self.load_success = True
            except:
                print_log("could not load {}".format(self.filename),
                    category="error")
        else:
            print_log("file missing: {}".format(self.filename),
                category="error")

    def get_setting(self, section, key):
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        else:
            print_log("{}:{} does not exist in {}"
                .format(section, key, self.filename), category="error")
            return None
