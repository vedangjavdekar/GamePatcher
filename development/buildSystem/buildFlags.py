class BuildFlags:
    def __init__(self) -> None:
        self.create_staging = True
        self.upload_server = True
        self.inc_ver = False
        self.inc_maj_ver = False
        self.write_staging_ver = True
        self.only_upload = False
        self.only_diff = False
        pass

    create_staging = True
    upload_server = True
    inc_ver = False
    inc_maj_ver = False
    write_staging_ver = True

    only_upload = False
    only_diff = False
