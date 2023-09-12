from ddv.ddv_file_info import DdvFileInfo


class DdvFileMeta:
    def __init__(self, files: [DdvFileInfo], bytes_processor) -> None:
        super().__init__()
        self.files = files
        self.version = "0.1"
        self.bytes_processor = bytes_processor
        self.original_total_size = 0
        self.packaged_total_size = 0

    def __str__(self) -> str:
        return str({"files": self.files, "version": self.version})
