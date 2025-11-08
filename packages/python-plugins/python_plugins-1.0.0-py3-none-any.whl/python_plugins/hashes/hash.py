import hashlib
import os.path


def hash_file(filename, algorithm="sha1"):
    if os.path.isfile(filename) is False:
        raise Exception("File not found for hash operation")

    sha_func = getattr(hashlib, algorithm)
    sha_obj = sha_func()

    with open(filename, "rb") as f:
        chunk = 0
        while chunk != b"":
            chunk = f.read(1024)
            sha_obj.update(chunk)

    return sha_obj.hexdigest()


def hash_text(text, algorithm="sha1"):
    # hashlib.md5(text).hexdigest()  # simple
    sha_func = getattr(hashlib, algorithm)
    sha_obj = sha_func()
    sha_obj.update(text)
    return sha_obj.hexdigest()
