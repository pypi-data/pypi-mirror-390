import random
import string
import os
import base64
import uuid
import secrets

# random.sample  # unique
# random.choices # not unique


def rand_digit(n):
    """随机数字"""
    return "".join(random.choices(string.digits, k=n))


def rand_letter(n: int):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def rand_sentence(n):
    return "".join(
        random.choices(string.ascii_letters + string.digits + " " * 10, k=n)
    ).strip()


def rand_uuid4():
    return str(uuid.uuid4())


def rand_token():
    return uuid.uuid4().hex


def secret_token():
    return secrets.token_hex(32)


def secret_token_16():
    return secrets.token_hex(16)


def rand_token_2(n):
    # replace '+/' with '1a'
    token = base64.b64encode(os.urandom(n), b"1a").decode()[0:n]
    return token
