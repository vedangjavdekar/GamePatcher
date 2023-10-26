import sys
from pathlib import Path
from buildInfo import VersionInfo
import pathUtils
import tarfile

import errorCodes


def create_archive(version: VersionInfo) -> bool:
    tar_file_path = pathUtils.get_tar_filepath(version)
    print(f"Creating TAR archive at {tar_file_path}...")
    try:
        with tarfile.open(tar_file_path, "w:gz") as archive_file:
            archive_file.add(
                pathUtils.get_shipping_build_dir(version), version.get_dir_name()
            )

            print("[SUCCESS]: TAR Archive created successfully!")
            return errorCodes.NO_ERROR
    except:
        return errorCodes.TAR_ERROR
