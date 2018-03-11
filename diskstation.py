# -*- coding: utf-8 -*-
import os, paths, platform
from printout import print_warning
import subprocess

def get_mount_points():
    return ['TV', 'FILM', 'MISC', 'BACKUP', 'DATA']

#Mount share
def mount(ds_share):
    if platform.system() != 'Linux':
        print("mount: Not on a Linux-system, quitting.")
        quit()
    dsip="192.168.0.101"
    home = os.getenv("HOME")
    opt = "credentials={}/.smbcredentials,iocharset=utf8,vers=3.0,rw,file_mode=0777,dir_mode=0777".format(home)
    ds_shares = get_mount_points()
    if ds_share == "all" or ds_share.upper() in ds_shares:
        for share in ds_shares:
            if share == ds_share.upper() or ds_share == "all":
                if ismounted(share):
                    print("{} is mounted at {}".format(share, get_mount_path(share)))
                    continue
                src = "//{}/{}".format(dsip, share)
                local_dest = "{}/smb/{}".format(home, share.lower())
                command = "sudo mount -t cifs {} {} -o {}".format(src, local_dest, opt)
                print("Mounting {} to {}".format(share, local_dest))
                #os.system(command)
                subprocess.call(["sudo", "mount", "-t", "cifs", src, local_dest, "-o", opt])
    else:
        print_warning("Invalid share: {}".format(ds_share))

# Check if share is already mounted
def ismounted(ds_share):
    ds_shares = get_mount_points()
    home = os.getenv("HOME")
    if ds_share.upper() in ds_shares :
        local_dest = os.path.join(home, "smb", ds_share.lower())
        subdirs = os.listdir(local_dest)
        if len(subdirs) > 1:
            return True
        return False
    else:
        print_warning("Invalid share: {}".format(ds_share))

# Get local mount path of ds share
def get_mount_path(ds_share):
    ds_shares = get_mount_points()
    home = os.getenv("HOME")
    if ds_share.upper() in ds_shares :
        local_dest = os.path.join(home, "smb", ds_share.lower())
        return local_dest
    else:
        print_warning("Invalid share: {}".format(ds_share))
        return None

# Print to console ifmounted
def print_ifmounted(ds_share):
    ds_shares = get_mount_points()
    for share in ds_shares:
        if ds_share == "all" or ds_share.lower() == share:
            if ismounted(share):
                print("{} is mounted at {}".format(share, get_mount_path(share)))
            else:
                print("{} is not mounted!".format(share))


#TODO: Unmount
#sudo umount ~/smb/tv
