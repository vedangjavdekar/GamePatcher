from pathlib import Path
import shutil
import subprocess
import requests
import tarfile
import json
import configparser
from os import remove

PARENT_DIR = Path(__file__).parent.absolute()
SEARCH_PATH = PARENT_DIR / "bin" / "data" / "version.ini"
BIN_PATH = PARENT_DIR / "bin"
TEMP_PATH = PARENT_DIR / "temp"
result = None

if SEARCH_PATH.exists():
    print("Get Patch")
    _config = configparser.ConfigParser()
    _config.read(SEARCH_PATH)
    version_string = _config["DEFAULT"]["version_string"]

    result = requests.get(
        f"http://localhost:3000/download?curr={version_string}&update=2.0"
    )

    match (result.headers["content-type"]):
        case "text/html":
            print(result.text)
        case "application/gzip":
            open(PARENT_DIR / "game.tar.gz", "wb").write(result.content)
            with tarfile.open(PARENT_DIR / "game.tar.gz") as file:
                print("extracting...")
                file.extractall(TEMP_PATH)
            remove(PARENT_DIR / "game.tar.gz")

            if Path(TEMP_PATH / "deleteFiles.json").exists():
                with open(TEMP_PATH / "deleteFiles.json", "r") as deleteFiles:
                    filesToDelete = json.load(deleteFiles)
                    for file in filesToDelete:
                        filePath = Path(BIN_PATH / file)
                        if filePath.exists():
                            filePath.unlink()
                Path(TEMP_PATH / "deleteFiles.json").unlink()

            shutil.copytree(TEMP_PATH, BIN_PATH, dirs_exist_ok=True)
            shutil.rmtree(TEMP_PATH)

else:
    result = requests.get("http://localhost:3000/download?update=version1.0")
    match (result.headers["content-type"]):
        case "text/html":
            print(result.text)
        case "application/gzip":
            open(PARENT_DIR / "game.tar.gz", "wb").write(result.content)
            with tarfile.open(PARENT_DIR / "game.tar.gz") as file:
                print("extracting...")
                file.extractall(BIN_PATH)
            remove(PARENT_DIR / "game.tar.gz")

subprocess.run(BIN_PATH / "Game.exe")
