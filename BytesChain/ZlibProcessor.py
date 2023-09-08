import zlib

from BytesChain.BytesAbstractProcessor import BytesAbstractProcessor


class ZlibProcessor(BytesAbstractProcessor):

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        return zlib.compress(bytes_data)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        return zlib.decompress(bytes_data)
