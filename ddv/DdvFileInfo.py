from enum import Enum


class FileType(Enum):
    DIR = 0
    File = 1


class DdvFileInfo:
    def __init__(self, name: str, size: int, type: FileType) -> None:
        super().__init__()
        self.name = name
        self.size = size
        self.type = type
        self.packed_size = 0
