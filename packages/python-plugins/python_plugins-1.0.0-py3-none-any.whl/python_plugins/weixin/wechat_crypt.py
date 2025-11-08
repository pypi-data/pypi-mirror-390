import base64
import string
import random
import hashlib
import struct
import socket

# from Crypto.Cipher import AES
# 使用 cryptography 替代 pycrypto 作为加密包
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ENCRYPT_TEXT_RESPONSE_TEMPLATE = """<xml>
<Encrypt><![CDATA[{msg_encrypt}]]></Encrypt>
<MsgSignature><![CDATA[{msg_signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""

def get_signature(arr):
    tmpstr = "".join(sorted(arr)).encode("utf-8")
    return hashlib.sha1(tmpstr).hexdigest()


class MessageCrypt:
    def __init__(self, appid, token, aeskey):
        self.appid = appid
        self.token = token
        self.key = base64.b64decode(aeskey + "=")

    def generate(self, encrypt, signature, timestamp, nonce):
        data = {
            "msg_encrypt": encrypt,
            "msg_signature": signature,
            "timestamp": timestamp,
            "nonce": nonce,
        }
        return ENCRYPT_TEXT_RESPONSE_TEMPLATE.format(**data)

    def get_encrypt_sig(self, msg, timestamp, nonce):
        msg_encrypt = WechatCrypt.encrypt(msg, self.key, self.appid)
        signature = get_signature([self.token, timestamp, nonce, msg_encrypt])
        return (msg_encrypt, signature)

    def encrypt_msg(self, msg, timestamp, nonce):
        msg_encrypt,signature = self.get_encrypt_sig(msg,timestamp,nonce)
        return self.generate(msg_encrypt, signature, timestamp, nonce)

    def decrypt_msg(self, timestamp, nonce, encrypt, msg_signature):
        signature = get_signature([self.token, timestamp, nonce, encrypt])
        if signature != msg_signature:
            return "ValidateSignatureError"
        decrypted = WechatCrypt.decrypt(encrypt, self.key, self.appid)
        return decrypted


class WechatCrypt:
    # mode = AES.MODE_CBC

    @classmethod
    def encrypt(cls, text, key, appid):
        # struct
        text_append = (
            (cls.get_random_str()).encode("utf-8")
            + struct.pack("I", socket.htonl(len(text.encode("utf-8"))))
            + text.encode("utf-8")
            + appid.encode("utf-8")
        )

        # 使用cryptography中的pad方法填补
        padded_data = PKCS7Encoder.padder(text_append)

        # 使用cryptography中加密
        iv = key[:16]
        encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # b64encode and decode('utf-8')
        text_base64 = base64.b64encode(ciphertext)
        return text_base64.decode("utf-8")

    @classmethod
    def decrypt(cls, text, key, appid):
        ciphertext = base64.b64decode(text)

        # 解密
        iv = key[:16]
        decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # 使用cryptography中的pad方法反填补
        plain_text = PKCS7Encoder.unpadder(plaintext_padded)

        # 解构
        content = plain_text[16:]
        xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
        xml = content[4 : xml_len + 4]
        from_appid = content[xml_len + 4 :]

        # 校验
        if from_appid == appid.encode("utf-8"):
            return xml
        else:
            raise Exception("ValidateAppidError")

    @classmethod
    def get_random_str(cls):
        rule = string.ascii_letters + string.digits
        str = random.sample(rule, 16)
        return "".join(str)


class PKCS7Encoder:
    block_size = 32

    @classmethod
    def padder(cls, data):
        """use cryptography, equal encode"""
        padder = padding.PKCS7(cls.block_size * 8).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    @classmethod
    def unpadder(cls, data):
        """use cryptography, equal decode"""
        unpadder = padding.PKCS7(cls.block_size * 8).unpadder()
        unpadded_data = unpadder.update(data) + unpadder.finalize()
        return unpadded_data

    @classmethod
    def encode(cls, text):
        text_length = len(text)
        amount_to_pad = cls.block_size - (text_length % cls.block_size)
        if amount_to_pad == 0:
            amount_to_pad = cls.block_size
        pad = chr(amount_to_pad)
        return text + (pad * amount_to_pad).encode("utf-8")

    @classmethod
    def decode(cls, decrypted):
        # pad = ord(decrypted[-1])  will error # for a bytes object b, b[0] will be an integer
        pad = decrypted[-1]
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]
