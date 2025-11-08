from python_plugins.crypto.cipher import AesCipher


def test_aes_cipher():
    msg = b"a secret message2"
    cipher = AesCipher()
    cipher.generate_key()
    cipher.generate_cipher()
    encryptor = cipher.create_encryptor()
    ct = encryptor.update(cipher.pad(msg)) + encryptor.finalize()
    decryptor = cipher.create_decryptor()
    unct = decryptor.update(ct) + decryptor.finalize()
    unpad_data = cipher.unpad(unct)
    assert msg == unpad_data
