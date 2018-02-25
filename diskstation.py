# -*- coding: utf-8 -*-
import os, paths, platform
from printout import print_warning

#Mount share
def mount(ds_share):
    if platform.system() != 'Linux':
        print("mount: Not on a Linux-system, quitting.")
        quit()
    dsip="192.168.0.101"
    opt = "credentials=$HOME/.smbcredentials,iocharset=utf8,vers=3.0," \
        "rw,file_mode=0777,dir_mode=0777"
    ds_shares = ['TV', 'FILM', 'MISC', 'BACKUP', 'DATA']
    if ds_share is 'all' or ds_share.upper() in ds_shares :
        for share in ds_shares:
            if share == ds_share.upper() or ds_share is 'all':
                if ismounted(share):
                    print("{} is already mounted.".format(share))
                    continue
                src = "//{}/{}".format(dsip, share)
                local_dest = "$HOME/smb/{}".format(share.lower())
                command = "sudo mount -t cifs {} {} -o {}".format(src, local_dest, opt)
                print("Mounting {} to {}".format(share), local_dest)
                os.system(command)
    else:
        print_warning("Invalid share: {}".format(ds_share))

# Check if share is already mounted
def ismounted(ds_share):
    ds_shares = ['TV', 'FILM', 'MISC', 'BACKUP', 'DATA']
    home = os.getenv("HOME")
    if ds_share.upper() in ds_shares :
        local_dest = os.path.join(home, "smb", ds_share.lower())
        subdirs = os.listdir(local_dest)
        if len(subdirs) > 1:
            return True
        return False
    else:
        print_warning("Invalid share: {}".format(ds_share))

#TODO: Unmount
#sudo umount ~/smb/tv
