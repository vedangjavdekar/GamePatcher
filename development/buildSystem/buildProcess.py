# Standard Library
from pathlib import Path
import os
import subprocess
import sys
import tarfile
import pprint
import json
import shutil
import copy
import requests
from datetime import datetime

# Custom Modules
import buildInfo
import app_version
import pathUtils

import fileDiffs
import tarUtils
import buildFlags
import errorCodes

# ==================== FLAGS ====================================

DEFAULT_FLAGS = buildFlags.BuildFlags()

DEFAULT_FLAGS.create_staging = True
DEFAULT_FLAGS.upload_server = True
DEFAULT_FLAGS.inc_ver = False
DEFAULT_FLAGS.inc_maj_ver = False
DEFAULT_FLAGS.write_staging_ver = True

DEFAULT_FLAGS.only_upload = False
DEFAULT_FLAGS.only_diff = False

# ========================================================


def load_version_info(build) -> buildInfo.Build:
    print("Fetching Current Version...")
    build.current_version = app_version.load(pathUtils.CURR_VERSION_FILE, True)

    print("\nFetching Prev Version...")
    build.prev_version = app_version.load(pathUtils.PREV_VERSION_FILE)


def get_directories(currentVersion: buildInfo.VersionInfo):
    # The previous build is located here
    src_root_dir = pathUtils.STAGING_DIR
    if not Path(src_root_dir).exists():
        os.mkdir(src_root_dir)

    # This is where the Latest build is located
    dst_root_dir = pathUtils.get_shipping_build_dir(currentVersion)

    return src_root_dir, dst_root_dir


def get_diff_directory_result(
    current_build: buildInfo.Build, src_root_dir: str, dst_root_dir: str
):
    ecode = errorCodes.NO_ERROR

    shouldDiffFolders = True
    if current_build.current_version.is_valid():
        print("[INFO]: Found Version: " + str(current_build.current_version))
    else:
        print("[ERROR]: Current Version not found.")

    if current_build.prev_version.is_valid():
        print("[INFO]: Found Version: " + str(current_build.prev_version))
    else:
        print("[WARNING]: Previous Version not found.")
        shouldDiffFolders = False

    if shouldDiffFolders:
        if not pathUtils.checkVersionBinDir(current_build.current_version):
            ecode = errorCodes.FILE_NOT_FOUND_ERROR
        if not pathUtils.checkVersionStagingDir(current_build.prev_version):
            ecode = errorCodes.FILE_NOT_FOUND_ERROR

        if ecode != errorCodes.NO_ERROR:
            return ecode

        print("Version Files found. Creating diffs...")
        temp_tar_path = pathUtils.get_temp_extract_dir(current_build.prev_version)
        with tarfile.open(
            pathUtils.get_tar_filepath(current_build.prev_version), "r"
        ) as prev_version_tar:
            prev_version_tar.extractall(pathUtils.STAGING_DIR)

        src_root_dir = temp_tar_path
    else:
        src_root_dir = pathUtils.STAGING_DIR + "\\version0_0"
        if not Path(src_root_dir).exists():
            os.mkdir(src_root_dir)

    print(f"SRC DIR: {src_root_dir}")
    print(f"DST DIR: {dst_root_dir}")

    fileDiffs.generate_folder_diff(current_build, src_root_dir, dst_root_dir)
    pprint.pprint(current_build.to_json())
    with open(
        pathUtils.get_manifest_filepath(current_build.current_version, True),
        "w",
    ) as manifestFile:
        json.dump(current_build.to_json(), manifestFile)

    shutil.rmtree(src_root_dir)
    print("[SUCCESS]: File Diff generated successfully!")
    return ecode


def increment_version(build: buildInfo.Build, incMaj: bool) -> str:
    cached_curr_version = copy.copy(build.current_version)
    version_needs_saving = False

    build.current_version.minor += 1
    version_needs_saving = True

    if incMaj:
        build.current_version.major += 1
        build.current_version.minor = 0
        version_needs_saving = True

    if version_needs_saving:
        build.current_version.create_version_string()
        app_version.save(build.current_version, pathUtils.CURR_VERSION_FILE)

        build.prev_version = cached_curr_version
        build.prev_version.create_version_string()
        app_version.save(build.prev_version, pathUtils.PREV_VERSION_FILE)

    return errorCodes.NO_ERROR, version_needs_saving


def upload_build_to_server(version: buildInfo.VersionInfo):
    print(f"Uploading {version.version_string} to the server...")
    build_manifest_path = pathUtils.get_manifest_filepath(version)
    tar_file_path = pathUtils.get_tar_filepath(version)

    print(f"build manifest path: {build_manifest_path}")
    print(f"tar path: {tar_file_path}")

    try:
        res = requests.post(
            "http://localhost:3000/builds",
            data={
                "VersionString": version.version_string,
                "ReleaseDate": (datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
            },
            files={
                "build_manifest": (
                    "build_manifest.json",
                    open(build_manifest_path, "rb"),
                    "application/json",
                ),
                "data": (
                    version.get_dir_name() + pathUtils.ARCHIVE_FILE_EXT,
                    open(tar_file_path, "rb"),
                    "application/gzip",
                ),
            },
        )

        print(res.json())

    except requests.exceptions.RequestException as e:
        print("[ERROR]: There was an error fulfilling the request. Aborting. ")
        return errorCodes.UPLOAD_ERROR
    return errorCodes.NO_ERROR


if __name__ == "__main__":
    _flags = DEFAULT_FLAGS

    current_build = buildInfo.Build()
    load_version_info(current_build)

    src_root_dir, dst_root_dir = get_directories(current_build.current_version)

    if _flags.only_diff:
        get_diff_directory_result(current_build, src_root_dir, dst_root_dir)
        sys.exit()

    if _flags.create_staging and not _flags.only_upload:
        if not dst_root_dir:
            print(
                f"[ERROR]: Shipping build for {current_build.current_version.version_string} not found. Make sure you have built the project in Shipping configuration."
            )
            sys.exit()

        shouldDiffFolders = True
        if current_build.current_version.is_valid():
            print("Found Version: " + str(current_build.current_version))
        else:
            print("Current Version not found.")

        if current_build.prev_version.is_valid():
            print("Found Version: " + str(current_build.prev_version))
        else:
            print("Previous Version not found.")
            shouldDiffFolders = False

        if shouldDiffFolders:
            assert pathUtils.checkVersionBinDir(current_build.current_version)
            assert pathUtils.checkVersionStagingDir(current_build.prev_version)
            print("Version Files found. Creating diffs...")
            temp_tar_path = pathUtils.get_temp_extract_dir(current_build.prev_version)
            with tarfile.open(
                pathUtils.get_tar_filepath(current_build.prev_version), "r"
            ) as prev_version_tar:
                prev_version_tar.extractall(pathUtils.STAGING_DIR)

            src_root_dir = temp_tar_path
            pass
        else:
            src_root_dir = pathUtils.STAGING_DIR + "\\version0_0"
            if not Path(src_root_dir).exists():
                os.mkdir(src_root_dir)

        print(f"SRC DIR: {src_root_dir}")
        print(f"DST DIR: {dst_root_dir}")

        fileDiffs.generate_folder_diff(current_build, src_root_dir, dst_root_dir)
        pprint.pprint(current_build.to_json())
        with open(
            pathUtils.get_manifest_filepath(current_build.current_version, True),
            "w",
        ) as manifestFile:
            json.dump(current_build.to_json(), manifestFile)

        shutil.rmtree(src_root_dir)

        if (
            tarUtils.create_archive(current_build.current_version)
            == errorCodes.NO_ERROR
        ):
            print("Archive Created successfully!")
        else:
            print("Error creating the archive... Aborting.")
            sys.exit()

    if _flags.upload_server or _flags.only_upload:
        upload_build_to_server(current_build.current_version)

    if _flags.create_staging and not _flags.only_upload:
        cached_curr_version = copy.copy(current_build.current_version)
        version_needs_saving = False
        if _flags.inc_ver:
            current_build.current_version.minor += 1
            version_needs_saving = True
        if _flags.inc_maj_ver:
            current_build.current_version.major += 1
            current_build.current_version.minor = 0
            version_needs_saving = True

        if version_needs_saving:
            current_build.current_version.create_version_string()
            app_version.save(current_build.current_version, pathUtils.CURR_VERSION_FILE)

        if _flags.write_staging_ver:
            current_build.prev_version = cached_curr_version
            current_build.prev_version.create_version_string()
            app_version.save(current_build.prev_version, pathUtils.PREV_VERSION_FILE)

        subprocess.run(["./GenerateProjectFiles.bat"], stdout=sys.stdout)
