#!/usr/bin/python3

import os, sys

class Goto(object):
    """ Stores 'goto-locations' """
    def __init__(self, shortcut):
        self.shortcut = shortcut
        self.destinations = []

    def add_destination(self, destination):
        """ Adds an alternative goto destination,
        that can be used if primary is missing """
        self.destinations.append(destination)

    def get_shortcut(self):
        """ Returns the shortcut of the Goto """
        return self.shortcut

    def get_path(self):
        """ Returns the first valid destination,
        stored in Location. None is returned if
        no existing path is found """
        for dest in self.destinations:
            if os.path.exists(dest):
                return dest
        return None

HOME = os.path.expanduser("~")
LOCS = {"dl" : [os.path.join(HOME, "downloads"), os.path.join(HOME, "Downloads")],
        "code" : [os.path.join(HOME, "code")],
        "film" : [os.path.join(HOME, "smb", "film")],
        "tv" : [os.path.join(HOME, "smb", "tv")]}

GOTOS = []
ARGUMENT = None

for sc in LOCS:
    g = Goto(sc)
    for d in LOCS[sc]:
        g.add_destination(d)
    GOTOS.append(g)

if len(sys.argv) > 1:
    ARGUMENT = sys.argv[1]
    for goto in GOTOS:
        if ARGUMENT == goto.get_shortcut():
            print(goto.get_path())
