import gzip
from typing import Type

import EncUtil
import config
from ddv.DdvFileInfo import DdvFileInfo


class BytesProcessor:
    def __init__(self, next_processor: Type['BytesProcessor']) -> None:
        super().__init__()
        self.next_processor = next_processor

    def pack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        pass

    def unpack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        pass


class PlainProcessor(BytesProcessor):
    def __init__(self, next_processor: Type['BytesProcessor']) -> None:
        super().__init__(next_processor)

    def pack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        return bytes_data

    def unpack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        return bytes_data


class GzipProcessor(BytesProcessor):
    def __init__(self, next_processor: Type['BytesProcessor']) -> None:
        super().__init__(next_processor)

    def pack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        return gzip.compress(bytes_data)

    def unpack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        return gzip.decompress(bytes_data)


class EncryptProcessor(BytesProcessor):
    def __init__(self, next_processor: Type['BytesProcessor']) -> None:
        super().__init__(next_processor)
        self.enc_util = EncUtil.EncUtil(config.password)

    def pack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        return self.enc_util.encrypt_bytes(bytes_data)

    def unpack_process(self, bytes_data: bytes, file_info: DdvFileInfo) -> bytes:
        return self.enc_util.decrypt_bytes(bytes_data)
