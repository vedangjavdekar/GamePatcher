import version
import sys
from pathlib import Path

print(Path().absolute())

with open("buildSystem/templates/version.template") as version_file:
    file_string = "".join(version_file.readlines())
    formatted = file_string.format(major=version.major,minor=version.minor,string=version.version_string)

    with open(sys.argv[1],'w') as header_file:
        header_file.write(formatted)
