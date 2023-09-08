import os.path
import sys
from decimal import Decimal, ROUND_HALF_EVEN

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from tqdm import tqdm

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


import config


class EncUtil:

    def __init__(self, passwd: str, buffer_size: int = 1024 * 1024 * 100) -> None:
        super().__init__()
        self.buffer_size = buffer_size
        self.key = self.generate_key(passwd)
        self.nonce = os.urandom(16)
        self.cipher = Cipher(algorithms.ChaCha20(self.key.encode("utf-8"), self.nonce), mode=None,
                             backend=default_backend())

    @staticmethod
    def generate_key(passwd: str) -> str:
        # 使用 PBKDF2HMAC 从种子生成密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            iterations=100000,  # 可以自行调整迭代次数
            salt=b"salt",
            length=16  # 生成 256 位的密钥
        )
        return kdf.derive(passwd.encode("utf-8")).hex()

    def encrypt_file(self, file: str, output: str):

        if os.path.islink(file):
            realpath = os.path.realpath(file)
            if not os.path.exists(realpath):
                raise Exception("符号链接指向的文件不存在")
            file = realpath
        # 创建一个加密器
        encrypt_util = self.cipher.encryptor()
        progress_bar = None
        if config.enable_progress:
            progress_bar = tqdm(total=100, desc="" + file + " --> Processing encrypt", file=sys.stderr)
        with open(file, "rb") as old, open(output, "wb") as new:
            new.write(self.nonce)
            count = 0
            while True:
                old_file = old.read(self.buffer_size)
                if not old_file:
                    break
                count += len(old_file)
                encrypted = encrypt_util.update(old_file)
                enc_len = len(encrypted)
                new.write(enc_len.to_bytes(4, "big"))
                new.write(encrypted)

                if progress_bar:
                    progress = Decimal(count / os.path.getsize(file)) * 100
                    progress = progress.quantize(Decimal('0'), rounding=ROUND_HALF_EVEN)
                    progress_bar.n = int(progress)

            new.write(encrypt_util.finalize())
        if progress_bar:
            progress_bar.close()
        # log.debug("初始大小：%d，加密后大小：%d，", os.path.getsize(file), os.path.getsize(output))

    def decrypt_file(self, file: str, output: str):
        progress_bar = None
        if config.enable_progress:
            progress_bar = tqdm(total=100, desc="" + file + " --> Processing decrypt", file=sys.stderr)
        with open(file, "rb") as old, open(output, "wb") as new:
            # 创建一个解密器
            self.nonce = old.read(16)
            self.cipher = Cipher(algorithms.ChaCha20(self.key.encode("utf-8"), self.nonce), mode=None,
                                 backend=default_backend())
            decrypt_util = self.cipher.decryptor()
            count = 0
            while True:
                len_mark = old.read(4)
                if not len_mark:
                    break
                count += len(len_mark)
                size = int.from_bytes(len_mark, "big")
                old_trunk = old.read(size)
                count += len(old_trunk)
                dec = decrypt_util.update(old_trunk)
                new.write(dec)

                if progress_bar:
                    progress = Decimal(count / os.path.getsize(file)) * 100
                    progress = progress.quantize(Decimal('0'), rounding=ROUND_HALF_EVEN)
                    progress_bar.n = int(progress)
                    progress_bar.refresh()
            new.write(decrypt_util.finalize())
        pass

    def encrypt_bytes(self, chunk: bytes):
        # 创建一个加密器
        encrypt_util = self.cipher.encryptor()
        enc_data = encrypt_util.update(chunk)
        enc_data += encrypt_util.finalize()
        return enc_data

    def decrypt_bytes(self, chunk: bytes):
        # 创建一个加密器
        decrypt_util = self.cipher.decryptor()
        data = decrypt_util.update(chunk)
        data += decrypt_util.finalize()
        return data

