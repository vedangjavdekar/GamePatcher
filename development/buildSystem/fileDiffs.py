from pathlib import Path
import buildInfo

from filecmp import dircmp

import os.path
from os import listdir
from os.path import isfile, isdir, join


def get_all_files(mypath, ignore=None):
    fs = []
    for f in listdir(mypath):
        if isdir(join(mypath, f)):
            ks = get_all_files(join(mypath, f))
            fs.extend(ks)
        if isfile(join(mypath, f)):
            if ignore and f in ignore:
                continue
            fs.append(join(mypath, f))
    return fs


# reference: http://docs.python.org/library/filecmp.html
def get_diff_files(current_build: buildInfo.Build, src_root_dir, dst_root_dir, dcmp):
    for name in dcmp.left_only:
        fname = dcmp.left + "\\" + name
        if isdir(fname):
            res = get_all_files(fname, dcmp.ignore)
            for f in res:
                fsize = os.path.getsize(f)
                fpath = str(Path(f).relative_to(src_root_dir))
                current_build.deleted_files.append(
                    {"path": fpath, "size": fsize, "action": "delete"}
                )
        else:
            fsize = os.path.getsize(fname)
            fpath = str(Path(fname).relative_to(src_root_dir))
            current_build.deleted_files.append(
                {"path": fpath, "size": fsize, "action": "delete"}
            )

    for name in dcmp.right_only:
        fname = dcmp.right + "\\" + name
        if isdir(fname):
            res = get_all_files(fname, dcmp.ignore)
            for f in res:
                fsize = os.path.getsize(f)
                fpath = str(Path(f).relative_to(dst_root_dir))
                current_build.added_files.append(
                    {"path": fpath, "size": fsize, "action": "add"}
                )
        else:
            fsize = os.path.getsize(fname)
            fpath = str(Path(fname).relative_to(dst_root_dir))
            current_build.added_files.append(
                {"path": fpath, "size": fsize, "action": "add"}
            )

    for name in dcmp.diff_files:
        abs_path = dcmp.right + "\\" + name
        fsize = os.path.getsize(abs_path)
        fpath = str(Path(abs_path).relative_to(dst_root_dir))
        current_build.added_files.append(
            {"path": fpath, "size": fsize, "action": "modify"}
        )

    for sub_dcmp in dcmp.subdirs.values():
        get_diff_files(current_build, src_root_dir, dst_root_dir, sub_dcmp)


def generate_folder_diff(
    current_build: buildInfo.Build, src_root_dir: str, dst_root_dir: str
):
    dcmp = dircmp(src_root_dir, dst_root_dir)
    get_diff_files(current_build, src_root_dir, dst_root_dir, dcmp)
