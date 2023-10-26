class VersionInfo:
    def __init__(self):
        self.major = 0
        self.minor = 0
        self.version_string = ""
        self.was_major_update = False

    def __str__(self) -> str:
        return f"VERSION[major: {self.major}, minor: {self.minor}, versionString: {self.version_string}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionInfo):
            return False

        return self.major == other.major and self.minor == other.minor

    def get_dir_name(self) -> str:
        return f"version{self.major}_{self.minor}"

    def is_valid(self) -> bool:
        return not (self.major == 0 and self.minor == 0)

    def create_version_string(self):
        self.version_string = f"version{self.major}.{self.minor}"

    major = 0
    minor = 0
    version_string = ""


class Build(object):
    def __init__(self):
        self.added_files = []
        self.deleted_files = []
        self.current_version = VersionInfo()

    def to_json(self):
        obj = {}
        obj["version_major"] = self.current_version.major
        obj["version_minor"] = self.current_version.minor
        obj["version_str"] = self.current_version.version_string
        obj["added_files"] = self.added_files
        obj["deleted_files"] = self.deleted_files
        return obj

    current_version = VersionInfo()
    prev_version = VersionInfo()
    added_files = []
    deleted_files = []
