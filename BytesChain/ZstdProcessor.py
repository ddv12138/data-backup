import pyzstd

from BytesChain.BytesAbstractProcessor import BytesAbstractProcessor


class ZstdProcessor(BytesAbstractProcessor):

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        return pyzstd.compress(bytes_data)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        return pyzstd.decompress(bytes_data)
