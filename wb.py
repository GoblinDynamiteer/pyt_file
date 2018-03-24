# -*- coding: utf-8 -*-
import subprocess, shlex, os, paths, filetools
from printout import print_script_name as psn
from printout import print_color_between as pcb
from printout import print_no_line as pnl
from printout import print_error
from datetime import datetime
import db_mov as movie_database

db = movie_database.database()

def print_log(string, category=None):
    script = os.path.basename(__file__)
    psn(script, "", endl=False) # Print script name
    if category == "error":
        print_error("Error: ", endl=False)
    if string.find('[') >= 0 and string.find(']') > 0:
        pcb(string, "blue")
    else:
        if string != "":
            print(string)

class file_list:
    def __init__(self, raw_data):
        self.raw_data = raw_data #Raw data from subprocess out
        self.raw_lines = self._raw_data_to_lines(raw_data)
        self.line_data = [] #empty list
        for line in self.raw_lines:
            d = self._line_to_dict(line)
            if d:
                self.line_data.append(d)

    def _print_list(self):
        for line in self.line_data:
            dtstr = line['date'].strftime("%Y-%m-%d %H:%M:%S")
            print_log("")   # print script name
            pnl(dtstr)      # print date string
            if line['in_db']:
                pcb(" [indb]", "green", endl=False)
            else:
                pcb(" [nodb]", "yellow", endl=False)
            if line['guessed_type']:
                pcb("[{}]".format(line['guessed_type'][0]), "green", endl=False)
            else:
                pcb("[{}]".format("-"), "red", endl=False)
            pcb("[ {} ]".format(line['name']), "blue")


    def _raw_data_to_lines(self, raw_data):
        lines = str(raw_data).split("\\n")
        return lines

    def _line_to_dict(self, raw_line):
        splits = raw_line.split()
        if len(splits) < 8:
            return None
        dt_str = "{} {}".format(splits[5], splits[6])
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        name = splits[7]
        return {'name': name, 'date': dt, 'in_db' : db.exists(name),
                'guessed_type' : filetools.guess_folder_type(name)}

class ls_command:
    def __init__(self, directory, remote=False):
        self.dir = directory
        self.ssh_server = remote
        self.command = self._generate_command()
        self.args = self._command_to_args(self.command)
        self.output = self._run()
        self.files = file_list(self.output)

    def print_files(self):
        self.files._print_list()

    def _generate_command(self):
        lsc = "ls -trl --time-style=\"+%Y-%m-%d %H:%M\" {}".format(self.dir)
        if self.ssh_server:
            lsc = "ssh {} {}".format(self.ssh_server, lsc)
        return lsc

    def _command_to_args(self, command):
        arg = shlex.shlex(command)
        arg.quotes = '"'
        arg.whitespace_split = True
        arg.commenters = ''
        return list(arg)

    def _run(self):
        print_log("running command: [ {} ]".format(self.command))
        process = subprocess.Popen(self.args, stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

    def print_info(self):
        print_log("command: [ {} ]".format(self.command))
        print_log("args: [ {} ]".format(self.args))

def wbnew():
    lsc = ls_command("~/files", remote="wb")
    lsc.print_files()
