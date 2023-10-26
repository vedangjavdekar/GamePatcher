import pathUtils
import app_version
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please provide the cpp and lua filepaths for creating the templates.")
        sys.exit()

    version = app_version.load(pathUtils.CURR_VERSION_FILE, True)

    with open(
        pathUtils.BUILD_SYS_DIR + "\\templates\\versionCPP.template", "r"
    ) as version_file:
        file_string = "".join(version_file.readlines())
        formatted = file_string.format(
            major=version.major,
            minor=version.minor,
            string=version.version_string,
        )

        with open(sys.argv[1], "w") as header_file:
            header_file.write(formatted)

    with open(
        pathUtils.BUILD_SYS_DIR + "\\templates\\versionLUA.template", "r"
    ) as version_file:
        file_string = "".join(version_file.readlines())
        formatted = file_string.format(major=version.major, minor=version.minor)

        with open(sys.argv[2], "w") as header_file:
            header_file.write(formatted)
