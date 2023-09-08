import gzip

from BytesChain.BytesAbstractProcessor import BytesAbstractProcessor


class GzipProcessor(BytesAbstractProcessor):

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        return gzip.compress(bytes_data)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        return gzip.decompress(bytes_data)