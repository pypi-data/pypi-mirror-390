import base64
from cryptography.hazmat.primitives import padding
from cryptography.fernet import Fernet


def generate_fernet_key(key) -> bytes:
    """see cryptography.fernet.Fernet.generate_key()

    :param key: _description_
    :raises ValueError: _description_
    :return: _description_
    """
    if isinstance(key, str):
        key = key.encode("utf-8")
    if not isinstance(key, bytes):
        raise ValueError
    if len(key) < 32:
        padder = padding.PKCS7(32 * 8).padder()
        key = padder.update(key) + padder.finalize()
    fernet_key = key[0:16] + key[16:32]
    return base64.urlsafe_b64encode(fernet_key)


def fernet_encrypt(key, txt) -> str:
    if isinstance(txt, str):
        txt = txt.encode("utf-8")
    fernet_key = generate_fernet_key(key)
    f = Fernet(fernet_key)
    token = f.encrypt(txt)
    return token.decode("utf-8")


def fernet_decrypt(key, token) -> str:
    if isinstance(token, str):
        token = token.encode("utf-8")
    fernet_key = generate_fernet_key(key)
    f = Fernet(fernet_key)
    decrypt_data = f.decrypt(token)
    return decrypt_data.decode("utf-8")
