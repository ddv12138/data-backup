from BytesChain.BytesAbstractProcessor import BytesAbstractProcessor


class PlainProcessor(BytesAbstractProcessor):

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        return bytes_data

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        return bytes_data