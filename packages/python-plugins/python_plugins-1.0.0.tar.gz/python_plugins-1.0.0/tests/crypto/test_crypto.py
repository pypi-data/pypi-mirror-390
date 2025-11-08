import pytest
import random
import base64
from python_plugins.random import rand_letter, rand_sentence
from python_plugins.random import secret_token, secret_token_16
from python_plugins.crypto.str_to_list import get_key
from python_plugins.crypto.str_to_list import encrypt_str_to_list, decrypt_list_to_str
from python_plugins.crypto import generate_fernet_key, fernet_encrypt, fernet_decrypt


class TestFetnet:
    def test_random_secret_token(self):
        token_1 = secret_token()
        # print(token_1)
        assert len(token_1) == 64
        token_2 = secret_token_16()
        # print(token_2)
        assert len(token_2) == 32

    def test_generate_fernet_key(self, fake):
        skey = fake.sentence()
        key = generate_fernet_key(skey)
        # print(key)
        decode_key = base64.urlsafe_b64decode(key)
        # print(decode_key)
        assert len(decode_key) == 32

    def test_fernet_encrypt_decrypt(self, fake):
        key = generate_fernet_key(fake.sentence())
        txt = fake.sentence()
        # print(key,txt)
        token = fernet_encrypt(key, txt)
        # print(token)
        assert isinstance(token, str)
        decrypt_txt = fernet_decrypt(key, token)
        # print(decrypt_txt)
        assert isinstance(decrypt_txt, str)
        assert txt == decrypt_txt


class TestStr2List:
    def test_get_key(self):
        password = rand_letter(random.randint(1, 50))
        key, safe_salt, times = get_key(password)
        decode_key = base64.urlsafe_b64decode(key)
        assert len(decode_key) == 32

    def test_encrypt_decrypt(self):
        s = rand_sentence(random.randint(10, 100))
        encrypted_list = encrypt_str_to_list(s)
        s2 = decrypt_list_to_str(encrypted_list)
        assert s == s2

    def test_encrypt_decrypt_with_password(self):
        s = rand_sentence(random.randint(10, 100))
        password = rand_letter(16)
        encrypted_list = encrypt_str_to_list(s, password)
        with pytest.raises(Exception):
            s1 = decrypt_list_to_str([None] + encrypted_list[1:])
        s2 = decrypt_list_to_str(encrypted_list, password)
        assert s == s2
        s3 = decrypt_list_to_str([None] + encrypted_list[1:], password)
        assert s == s3
