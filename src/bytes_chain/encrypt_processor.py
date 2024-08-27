import enc_util
import config
from bytes_chain.bytes_abstract_processor import BytesAbstractProcessor
from log_util import log

class EncryptProcessor(BytesAbstractProcessor):
    enc_util = enc_util.EncUtil(config.password,config.password.encode("utf-8"),(config.password*3).encode("utf-8"))

    def __pack_process__(self, bytes_data: bytes) -> bytes:
        log.debug(f"EncryptProcessor packing {bytes_data}")
        return self.enc_util.encrypt_bytes(bytes_data)

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        log.debug(f"EncryptProcessor unpacking {bytes_data}")
        return self.enc_util.decrypt_bytes(bytes_data)