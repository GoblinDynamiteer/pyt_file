# -*- coding: utf-8 -*-
import os, paths, platform
from config import configuration_manager as cfg
import subprocess
from printout import print_class as pr

pr = pr(os.path.basename(__file__))
_config = cfg()

def get_mount_points():
    return ['TV', 'FILM', 'MISC', 'BACKUP', 'DATA', 'DOCEDU', 'AUDIO']

def get_mount_dest():
    return _config.get_setting("path", "dsmount")

def get_home():
    return _config.get_setting("path", "home")

def _get_credentials_file(share):
    if share == 'Rest':
        return get_home() + ".smbcredentials_drb"
    return get_home() + ".smbcredentials"

def _print_error_invalid_share(string):
    pr.error(f"invalid share: [{string}]")

#Mount share
def mount(ds_share):
    if platform.system() != 'Linux':
        pr.error("mount: Not on a Linux-system, quitting.")
        quit()
    dsip="192.168.0.101"
    mount_dest = get_mount_dest()
    ds_shares = get_mount_points()
    if ds_share == "all" or ds_share.upper() in ds_shares:
        for share in ds_shares:
            if share == ds_share.upper() or ds_share == "all":
                if ismounted(share):
                    pr.info(f"{share} is mounted at {get_mount_path(share)}")
                    continue
                cred_file = _get_credentials_file(share)
                opt = f"credentials={cred_file},iocharset=utf8,vers=3.0,rw,file_mode=0777,dir_mode=0777"
                src = f"//{dsip}/{share}"
                local_dest = f"{mount_dest}{share.lower()}"
                command = f"sudo mount -t cifs {src} {local_dest} -o {opt}"
                pr.info(f"mounting {share} to {local_dest}")
                #os.system(command)
                subprocess.call(["sudo", "mount", "-t", "cifs", src, local_dest, "-o", opt])
    else:
        _print_error_invalid_share(ds_share);

# Check if share is already mounted
def ismounted(ds_share):
    if ds_share.lower() == 'rest':
        return
    ds_shares = get_mount_points()
    mount_dest = get_mount_dest()
    if ds_share.upper() in ds_shares :
        local_dest = os.path.join(mount_dest, ds_share.lower())
        subdirs = os.listdir(local_dest)
        if len(subdirs) > 1:
            return True
        return False
    else:
        _print_error_invalid_share(ds_share);

# Get local mount path of ds share
def get_mount_path(ds_share):
    if ds_share.lower() == 'rest':
        return
    ds_shares = get_mount_points()
    mount_dest = get_mount_dest()
    if ds_share.upper() in ds_shares :
        local_dest = os.path.join(mount_dest, ds_share.lower())
        return local_dest
    else:
        _print_error_invalid_share(ds_share);
        return None

# Print to console ifmounted
def print_ifmounted(ds_share):
    ds_shares = get_mount_points()
    for share in ds_shares:
        if share == 'Rest':
            continue
        if ds_share == "all" or ds_share.lower() == share:
            if ismounted(share):
                pr.info(f"{share} is mounted at {get_mount_path(share)}")
            else:
                pr.info(f"{share} is not mounted!")


#TODO: Unmount
#sudo umount ~/smb/tv
