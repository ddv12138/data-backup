from ddv.DdvFileInfo import DdvFileInfo


class DdvFileMeta:
    def __init__(self, files: [DdvFileInfo]) -> None:
        super().__init__()
        self.files = files
        self.version = "0.1"

    def __str__(self) -> str:
        return str({"files": self.files, "version": self.version})
