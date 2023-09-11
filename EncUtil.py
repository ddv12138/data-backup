import random
import string

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


def generate_nonce() -> bytes:
    return "".join(random.sample(string.ascii_letters + string.digits, 16)).encode("utf-8")


def generate_salt() -> bytes:
    return "".join(random.sample(string.ascii_letters + string.digits, 8)).encode("utf-8")


class EncUtil:

    def __init__(self, passwd: str, salt: bytes = generate_salt(), nonce: bytes = generate_nonce()) -> None:
        super().__init__()
        self.salt = salt
        self.nonce = nonce
        self.passwd = passwd
        self.key = self.generate_key(passwd)
        self.cipher = Cipher(algorithms.ChaCha20(self.key.encode("utf-8"), self.nonce), mode=None,
                             backend=default_backend())

    def generate_key(self, passwd: str) -> str:
        # 使用 PBKDF2HMAC 从种子生成密钥
        _kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            iterations=10000,  # 可以自行调整迭代次数
            salt=self.salt,
            length=16  # 生成 256 位的密钥
        )
        return _kdf.derive(passwd.encode("utf-8")).hex()

    def encrypt_bytes(self, chunk: bytes):
        # 创建一个加密器
        encrypt_util = self.cipher.encryptor()
        enc_data = encrypt_util.update(chunk)
        enc_data += encrypt_util.finalize()
        return self.salt + self.nonce + enc_data

    def decrypt_bytes(self, chunk: bytes):
        self.salt = chunk[0:8]
        self.nonce = chunk[8:24]
        self.key = self.generate_key(self.passwd)
        self.cipher = Cipher(algorithms.ChaCha20(self.key.encode("utf-8"), self.nonce), mode=None,
                             backend=default_backend())
        decrypt_util = self.cipher.decryptor()
        data = decrypt_util.update(chunk[24:])
        data += decrypt_util.finalize()
        return data
