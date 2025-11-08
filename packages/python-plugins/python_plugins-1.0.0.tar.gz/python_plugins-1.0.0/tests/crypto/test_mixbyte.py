import pytest
import os
import os.path as op
import hashlib
from python_plugins.crypto.mixbyte import MixByte


def get_tmp_path():
    parent_dir = op.realpath(op.dirname(__file__))
    tmp_path = op.realpath(op.join(parent_dir, "..", "tmp"))
    return tmp_path


class TestMixByte:
    def test_generate_password(self):
        mix = MixByte()
        pwd=mix.generate_password()
        assert isinstance(pwd,str)
        assert len(pwd) == 32
        pwd=mix.generate_password(10)
        assert isinstance(pwd,str)
        assert len(pwd) == 10

    def test_int_to_nbytes(self):
        mix = MixByte()
        for v in (0, 1, 255, 256, 65535, 2**24 - 1):
            b = mix.int_to_nbytes(v)
            assert len(b) == 2
            assert isinstance(b[0], bytes)
            assert isinstance(b[1], bytes)
            assert int.from_bytes(b[0]) == len(b[1])
            assert int.from_bytes(b[1]) == v

    def test_mix_tag(self):
        mix = MixByte()
        tag = mix.create_mix_tag()
        assert mix.check_mix_tag(tag) is True

    def test_hash_block(self):
        mix = MixByte()
        data = os.urandom(500)
        hash_block = mix.create_hash_block(data)
        (hash_method, hash_body) = mix.parse_hash_block(hash_block)
        assert hash_method == "md5"
        assert len(hash_body) == 16

    def test_pwd_block(self):
        mix = MixByte()
        for pwd in (b"1", b"a" * 32, b"a" * 128):
            block = mix.create_pwd_block(pwd)
            assert mix.parse_pwd_block(block) == pwd
        for pwd in (b"", b"a" * 129):
            with pytest.raises(Exception):
                block = mix.create_pwd_block(pwd)

    def test_build_tail_link_blocks(self):
        mix = MixByte()
        data = os.urandom(500)
        pwd = b"abce" * 8
        blocks = [
            {"name": "hash", "body": mix.create_hash_block(data)},
            {"name": "pwd", "body": mix.create_pwd_block(pwd)},
        ]
        tail_bytes = mix.build_tail_link_blocks(blocks)
        new_data = data + tail_bytes
        result = mix.parse_tail_link_blocks(new_data)
        # print(result)
        assert result is not None
        assert isinstance(result, dict)
        assert result["pwd"] == pwd
        assert result["hash"][1] == getattr(hashlib, result["hash"][0])(data).digest()
        assert result["block_size"] == len(new_data) - len(data)

    def test_insert_bytes_to_binary(self):
        mix = MixByte()
        data = os.urandom(500)
        insert = os.urandom(32)
        new_data, start_pos = mix.mix_bytes_to_binary(data, insert)
        extracted = mix.extract_from_mixed_binary(new_data, start_pos)
        assert "insert" in extracted
        assert extracted["insert"] == insert
        assert "data" in extracted
        assert extracted["data"] == data

    def test_list_archive_mix(self):
        tmp_path = get_tmp_path()
        test_compress_file = op.join(tmp_path, "test.archive.mix")
        if os.path.exists(test_compress_file):
            mix = MixByte()
            result = mix.list_archive_mix(test_compress_file)
            print(result)
