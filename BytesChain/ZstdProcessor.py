import os

import pyzstd

from BytesChain.BytesAbstractProcessor import BytesAbstractProcessor


class ZstdProcessor(BytesAbstractProcessor):
    def __pack_process__(self, bytes_data: bytes) -> bytes:
        option = {pyzstd.CParameter.nbWorkers: os.cpu_count()}
        return pyzstd.compress(bytes_data,option)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        return pyzstd.decompress(bytes_data)
