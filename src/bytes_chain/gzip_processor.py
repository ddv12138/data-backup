import gzip

from bytes_chain.bytes_abstract_processor import BytesAbstractProcessor
from log_util import log

class GzipProcessor(BytesAbstractProcessor):

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        log.debug(f"GzipProcessor Packing {bytes_data}")
        return gzip.compress(bytes_data)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        log.debug(f"GzipProcessor Unpacking {bytes_data}")
        return gzip.decompress(bytes_data)