import sys
import currversion
from pathlib import Path
from filecmp import dircmp

import os.path
from os import listdir
from os.path import isfile, isdir, join

import json
import shutil
import tarfile

class Build(object):
    def __init__(self):
        self.added_files=[]
        self.deleted_files=[]

    def toJSON(self):
        obj={}
        obj["version"] = self.version
        obj["version_str"] = self.version_str
        obj["added_files"] = self.added_files
        obj["deleted_files"] = self.deleted_files
        return obj

    version=1.0
    version_str=""
    added_files=[]
    deleted_files=[]

current_build = Build()

# ========================================================

def generate_build_manifest():
    return "-b" in sys.argv[1:]

def generate_tar_archive():
    return "-t" in sys.argv[1:]

def update_version_file():
    return "-v" in sys.argv[1:]
# ========================================================

def get_all_files(mypath):
	fs = []
	for f in listdir(mypath):
		if (isdir(join(mypath,f))):
			ks = get_all_files(join(mypath,f))
			fs.extend(ks)
		if isfile(join(mypath,f)) :
			fs.append(join(mypath,f))
	return fs


# reference: http://docs.python.org/library/filecmp.html
def get_diff_files(dcmp):
    for name in dcmp.left_only:
        fname = dcmp.left +"/" + name
        if isdir(fname):
            res = get_all_files(fname)
            for f in res:
                fsize = os.path.getsize(f)
                current_build.deleted_files.append({"path" : f ,"size" : fsize, "action" : "delete"})
        else:
            fsize = os.path.getsize(fname)
            current_build.deleted_files.append({"path" : fname ,"size" : fsize, "action" : "delete"})

    for name in dcmp.right_only:
        fname = dcmp.right +"/" + name
        if isdir(fname):
            res = get_all_files(fname)
            for f in res:
                fsize = os.path.getsize(f)
                fpath = f.split("Shipping")
                if len(fpath) > 1:
                    current_build.added_files.append({"path" : fpath[1] ,"size" : fsize, "action" : "add"})
        else:
            fsize = os.path.getsize(fname)
            fpath = fname.split("Shipping")
            if len(fpath) > 1:
                current_build.added_files.append({"path" : fpath[1] ,"size" : fsize, "action" : "add"})

    for name in dcmp.diff_files:
        abs_path = dcmp.right + "/" + name
        fsize = os.path.getsize(abs_path)
        fpath = abs_path.split("Shipping",1)
        if len(fpath) > 1:
            current_build.added_files.append({"path" : fpath[1], "size" : fsize, "action" : "modify"})

    for sub_dcmp in dcmp.subdirs.values():
        get_diff_files(sub_dcmp)

def checkVersionExists(major, minor):
    version_str = "version{0}_{1}".format(major,minor)
    print("Checking for version " + version_str + "...")
    if Path("../shipping/"+version_str+".tar").exists():
        print("Shipping build for current version found!")
        return True
    else:
        print("No files found for " + version_str)
        # TODO: Get it from server.
        return False


# Paths
curr_version_str = "version{major}_{minor}".format(major=currversion.major,minor=currversion.minor)
src_dir = "./bin/"+curr_version_str+"/Shipping"
dst_dir = "../shipping"
build_manifest_path = src_dir + "/" + "build_manifest.json"
tar_path = dst_dir + "/" + curr_version_str + ".tar"

if not Path(src_dir).exists():
    print(f"Shipping build not found at {src_dir}. Aborting.")
    sys.exit()

with open("../shipping/VERSION.txt","r+") as shipped_version:
    version_str = shipped_version.read()

    if version_str=="":
        print("No version has been shipped yet... No comparison required")
        

        dcmp = dircmp(dst_dir,src_dir) 
        get_diff_files(dcmp)
        current_build.deleted_files=[] # First build, nothing is deleted

    else:
        version_info = version_str.split(" ")
        if checkVersionExists(version_info[1], version_info[2]):
            tar_file_path = dst_dir+f"/version{version_info[1]}_{version_info[2]}.tar"
            extracted_file_path = dst_dir+f"/version{version_info[1]}_{version_info[2]}/"

            # TODO: Add VFS to mount the tar as is and treat it as a directory and compare it
            with tarfile.open(tar_file_path,"r") as prev_version:
                prev_version.extractall(dst_dir)
                dcmp = dircmp(extracted_file_path,src_dir) 
                get_diff_files(dcmp)
                shutil.rmtree(extracted_file_path)
        else:
            print("No build data found. Aborting")
            sys.exit()

    if generate_build_manifest():
        current_build.version = float(f"{currversion.major}.{currversion.minor}")
        current_build.version_str = curr_version_str

        with open(build_manifest_path,"w") as build_manifest:
            json.dump(current_build.toJSON(), build_manifest)

        fsize = os.path.getsize(build_manifest_path) 
        fpath = build_manifest_path.split("Shipping", 1)
        current_build.added_files.append({"path" : fpath[1], "size": fsize, "action" : "add"})

    print("Files Added/Modified:")
    for f in current_build.added_files:
        print(f)
    print("Files Deleted:")
    for f in current_build.deleted_files:
        print(f)

    if generate_tar_archive():
        with tarfile.open(tar_path, "w") as tar:
            tar.add(src_dir,arcname=curr_version_str)
    
    if update_version_file():
        shipped_version.seek(0)
        shipped_version.write(f"VERSION {currversion.major} {currversion.minor}")
    