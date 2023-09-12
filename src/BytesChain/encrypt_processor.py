import enc_util
import config
from BytesChain.bytes_abstract_processor import BytesAbstractProcessor


class EncryptProcessor(BytesAbstractProcessor):
    enc_util = EncUtil.EncUtil(config.password)

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        return self.enc_util.encrypt_bytes(bytes_data)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        return self.enc_util.decrypt_bytes(bytes_data)