from enum import Enum
from pathlib import Path
from buildInfo import VersionInfo
import os

# CONSTANTS
BUILD_SYS_DIR = str(Path(__file__).parent.absolute().resolve())
BIN_DIR = str(Path(BUILD_SYS_DIR + "\\..\\bin").absolute().resolve())
STAGING_DIR = str(Path(BUILD_SYS_DIR + "\\..\\..\\shipping").absolute().resolve())

# FILE PATHS
CURR_VERSION_FILE = BUILD_SYS_DIR + "\\config\\version.ini"
PREV_VERSION_FILE = STAGING_DIR + "\\version.ini"

# EXTENTIONS
ARCHIVE_FILE_EXT = ".tar.gz"
MANIFEST_FILE_EXT = ".json"


def get_shipping_build_dir(version: VersionInfo) -> str:
    dir_path = Path(BIN_DIR + f"\\version{version.major}_{version.minor}\\Shipping")

    if dir_path.exists():
        return str(dir_path.absolute().resolve())
    else:
        return ""


def get_temp_extract_dir(version: VersionInfo) -> str:
    return str(
        Path(STAGING_DIR + f"\\version{version.major}_{version.minor}")
        .absolute()
        .resolve()
    )


def get_tar_filepath(version: VersionInfo) -> str:
    return str(
        Path(STAGING_DIR + f"\\{version.get_dir_name()}{ARCHIVE_FILE_EXT}")
        .absolute()
        .resolve()
    )


def get_manifest_dir(version: VersionInfo, createDir=False) -> str:
    dir_path = get_shipping_build_dir(version)
    if dir_path:
        dir_path = Path(dir_path + "\\data")
        if not dir_path.exists() and createDir:
            os.mkdir(dir_path)
        return str(dir_path.absolute().resolve())
    return ""


def get_manifest_filepath() -> str:
    dir_path = Path(__file__).parent / "content"
    if not dir_path.exists():
        Path.mkdir(dir_path)

    fileName = "build_manifest" + MANIFEST_FILE_EXT
    dir_path = dir_path / fileName
    return str(dir_path.absolute().resolve())


def checkVersionStagingDir(version: VersionInfo):
    return Path(STAGING_DIR + f"\\{version.get_dir_name()}{ARCHIVE_FILE_EXT}").exists()


def checkVersionBinDir(version: VersionInfo):
    return Path(get_shipping_build_dir(version)).exists()
