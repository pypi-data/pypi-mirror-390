import pytest
import os
import os.path as op
import filecmp
from python_plugins.random.random_str import rand_sentence
from python_plugins.crypto import encrypt_txtfile
from python_plugins.crypto import decrypt_txtfile

tmp_path = op.join(os.path.dirname(os.path.abspath(__file__)), "tmp")

path_1 = op.join(tmp_path, "test1.txt")
path_2 = op.join(tmp_path, "test2.txt")
path_3 = op.join(tmp_path, "test3.txt")
path_4 = op.join(tmp_path, "test4.txt")
path_5 = op.join(tmp_path, "test5.txt")


def _create_temp():
    if not op.exists(tmp_path):
        os.mkdir(tmp_path)
        return tmp_path


def safe_delete(path):
    try:
        if op.exists(path):
            os.remove(path)
    except:
        pass


def _remove_testfiles():
    safe_delete(path_1)
    safe_delete(path_2)
    safe_delete(path_3)
    safe_delete(path_4)
    safe_delete(path_5)

def test_crypto_file():
    create_tmp = _create_temp()
    if create_tmp:
        print(create_tmp)

    with open(path_1, "w") as f:
        f.write(rand_sentence(30))
        f.write(rand_sentence(30))

    encrypt_txtfile(path_1, path_2)
    # decrypt_txtfile(path_2)
    decrypt_txtfile(path_2, path_3)
    cmp_result = filecmp.cmp(path_1, path_3)
    assert cmp_result is True

    _remove_testfiles()

def test_crypto_file_with_password():

    with open(path_1, "w") as f:
        f.write(rand_sentence(30))
        f.write(rand_sentence(30))

    password = rand_sentence(10)
    encrypt_txtfile(path_1, path_2, password=password)
    with pytest.raises(Exception):
        decrypt_txtfile(path_2, path_3,password="")
    decrypt_txtfile(path_2, path_3, password=password)
    cmp_result = filecmp.cmp(path_1, path_3)
    assert cmp_result is True

    _remove_testfiles()

# pytest with `input()` must using `-s`
# pytest tests\test_crypt_file.py::test_crypto_file_with_password -s
@pytest.mark.skip
def test_crypto_file_with_input_password():

    with open(path_1, "w") as f:
        f.write(rand_sentence(30))
        f.write(rand_sentence(30))

    encrypt_txtfile(path_1, path_2, password='[input]')
    decrypt_txtfile(path_2, path_3)
    cmp_result = filecmp.cmp(path_1, path_3)
    assert cmp_result is True

    _remove_testfiles()
