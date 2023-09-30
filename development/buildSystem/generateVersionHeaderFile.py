import currversion
import sys
from pathlib import Path

with open("buildSystem/templates/versionCPP.template") as version_file:
    file_string = "".join(version_file.readlines())
    formatted = file_string.format(major=currversion.major,minor=currversion.minor,string=currversion.version_string)

    with open(sys.argv[1],'w') as header_file:
        header_file.write(formatted)

with open("buildSystem/templates/versionLUA.template") as version_file:
    file_string = "".join(version_file.readlines())
    formatted = file_string.format(major=currversion.major,minor=currversion.minor)

    with open('Version.lua','w') as header_file:
        header_file.write(formatted)