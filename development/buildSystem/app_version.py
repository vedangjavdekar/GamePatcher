from buildInfo import VersionInfo

from pathlib import Path
import configparser


# PRIVATE VARIABLES
_config = configparser.ConfigParser()


def load(filepath, createIfNotExists=False) -> VersionInfo:
    version = VersionInfo()

    fileExists = True
    if not Path(filepath).exists():
        fileExists = False
        if createIfNotExists:
            print("[WARN] : config file doesn't exist. Writing default config file.")
            version.major = 1
            version.minor = 0
            version.create_version_string()
            save(version, filepath)

    if fileExists:
        with open(filepath, "r") as configFile:
            _config.read(filepath)
            version.major = int(_config["DEFAULT"]["major"])
            version.minor = int(_config["DEFAULT"]["minor"])
            version.version_string = _config["DEFAULT"]["version_string"]
            print("[INFO] : config loaded successfully!")

    return version


def save(version: VersionInfo, filepath: str):
    _config["DEFAULT"]["major"] = str(version.major)
    _config["DEFAULT"]["minor"] = str(version.minor)
    _config["DEFAULT"]["version_string"] = version.version_string
    with open(filepath, "w") as configFile:
        _config.write(configFile)
