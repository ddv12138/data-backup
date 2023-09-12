import datetime
import os
import time

from bytes_chain.bytes_abstract_processor import BytesAbstractProcessor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

from enc_util import EncUtil


class AesEncProcessor(BytesAbstractProcessor):
    def __pack_process__(self, bytes_data: bytes) -> bytes:
        pass

    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        pass


def aes_encrypt(message):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message) + padder.finalize()
    iv = b'\x00' * 16  # 初始化向量，必须是16字节
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(ct)


def aes_decrypt(token):
    ct = base64.b64decode(token)
    iv = b'\x00' * 16  # 初始化向量，必须是16字节
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    data = decryptor.update(ct) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(data) + unpadder.finalize()
    return message


if __name__ == '__main__':
    util = EncUtil(passwd="123456")
    data = os.urandom(1 << 20)
    key = b"your_secret_key_"
    backend = default_backend()
    start = time.time()
    for _ in range(500):
        # util.encrypt_bytes(data)
        aes_encrypt(data)
    print(500 / (time.time() - start))
