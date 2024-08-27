import os

import pyzstd

from bytes_chain.bytes_abstract_processor import BytesAbstractProcessor
from log_util import log

class ZstdProcessor(BytesAbstractProcessor):
    def __pack_process__(self, bytes_data: bytes) -> bytes:
        log.debug(f"ZstdProcessor Packing {bytes_data}")
        option = {pyzstd.CParameter.nbWorkers: os.cpu_count()}
        return pyzstd.compress(bytes_data,option)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        log.debug(f"ZstdProcessor Unpacking {bytes_data}")
        return pyzstd.decompress(bytes_data)
