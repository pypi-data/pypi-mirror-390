import base64
import json
import time

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class WeixinBizDataCrypt:
    """Weixin Biz Data Crypt
    微信小程序服务端获取开放数据
    see https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/signature.html
    """

    def __init__(self, appid, sessionKey):
        self.appid = appid
        self.sessionKey = sessionKey

    def decrypt(self, data, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(data)
        iv = base64.b64decode(iv)

        decryptor = Cipher(
            algorithms.AES(sessionKey),
            modes.CBC(iv),
        ).decryptor()
        plaintext_padded = decryptor.update(encryptedData)
        plaintext_padded += decryptor.finalize()

        unpadded = self._unpad(plaintext_padded)
        decrypted = json.loads(unpadded)

        # 校验签名
        if decrypted["watermark"]["appid"] != self.appid:
            raise Exception("Invalid Buffer")

        return decrypted

    def encrypt(self, data, iv) -> str:
        # 添加watermark
        data["watermark"] = {"appid": self.appid, "timestamp": int(time.time())}
        nopadData = json.dumps(data).encode()
        sessionKey = base64.b64decode(self.sessionKey)
        iv = base64.b64decode(iv)

        encryptor = Cipher(
            algorithms.AES(sessionKey),
            modes.CBC(iv),
        ).encryptor()

        # see https://cryptography.io/en/latest/hazmat/primitives/padding/
        # 填补数据，满足block_size的倍数
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(nopadData)
        padded_data += padder.finalize()

        # 加密
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        # base64.b64encode -> str
        encrypted = base64.b64encode(encrypted).decode()
        return encrypted

    def _unpad(self, s):
        """cryptography.hazmat.primitives.padding.PKCS7(128).unpadder()的简化版本"""
        return s[: -ord(s[-1:])]
