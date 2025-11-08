import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class Pad:
    def pad(self, data, nbits=128):
        padder = padding.PKCS7(nbits).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def unpad(self, data, nbits=128):
        unpadder = padding.PKCS7(nbits).unpadder()
        unpadded_data = unpadder.update(data) + unpadder.finalize()
        return unpadded_data


class AesCipher(Pad):
    """Cipher with aes.
    For example::

        msg = b"a secret message"
        cipher = AesCipher()    
        cipher.generate_key()
        print(cipher.key,cipher.iv)
        cipher.generate_cipher()
        encryptor = cipher.create_encryptor()
        ct = encryptor.update(cipher.pad(msg)) + encryptor.finalize()
        decryptor = cipher.create_decryptor()
        unct = decryptor.update(ct) + decryptor.finalize()
        unpad_data = cipher.unpad(unct)

    """
    def __init__(self, key=None, iv=None):
        self.key = key
        self.iv = iv
        self.cipher = None

    def generate_key(self):
        self.key = os.urandom(32)
        self.iv = os.urandom(16)

    def generate_cipher(self):
        if (
            isinstance(self.key, bytes)
            and len(self.key) == 32
            and isinstance(self.iv, bytes)
            and len(self.iv) == 16
        ):
            self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))
        else:
            raise Exception("key or iv is wrong")

    def create_encryptor(self):
        if self.cipher is None:
            raise Exception("self.cipher is None")
        encryptor = self.cipher.encryptor()
        return encryptor

    def create_decryptor(self):
        if self.cipher is None:
            raise Exception("self.cipher is None")
        decryptor = self.cipher.decryptor()
        return decryptor
