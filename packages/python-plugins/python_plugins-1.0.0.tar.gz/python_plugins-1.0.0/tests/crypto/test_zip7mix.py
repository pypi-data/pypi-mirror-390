import pytest
import os
import os.path as op
import shutil
import filecmp
from python_plugins.crypto.zip7mix import Zip7Mix


def get_tmp_path():
    parent_dir = op.realpath(op.dirname(__file__))
    tmp_path = op.realpath(op.join(parent_dir, "..", "tmp"))
    return tmp_path


class TestZip7Mix:
    def test_zip7_available(self):
        zm = Zip7Mix()
        assert zm.z7_available is True

    def test_compress(self):
        tmp_path = get_tmp_path()
        test_file = op.join(tmp_path, "test.txt")
        test_out_dir = op.join(tmp_path, "out")
        test_compress_file = op.join(tmp_path, "test.txt.7z")
        test_uncompress_file = op.join(test_out_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)
        z7 = Zip7Mix()
        r_compress = z7.compress(test_file)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        # r_list = zm.list_archive(f_zip)
        # assert r_list[0] == "ok"
        r_uncompress = z7.uncompress(test_compress_file, test_out_dir)
        assert r_uncompress[0] == "ok"
        assert op.exists(test_uncompress_file)
        assert filecmp.cmp(test_file, test_uncompress_file) is True
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)

    def test_compress_with_password(self):
        tmp_path = get_tmp_path()
        test_file = op.join(tmp_path, "test.txt")
        test_out_dir = op.join(tmp_path, "out")
        test_compress_file = op.join(tmp_path, "test.txt.7z")
        test_uncompress_file = op.join(test_out_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)
        z7 = Zip7Mix()
        pwd = "abcdefghijklm"
        r_compress = z7.compress(test_file, pwd=pwd)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        # fail if without pwd
        # r_uncompress = z7.uncompress(test_compress_file, test_out_dir)
        # assert r_uncompress[0] == "fail"
        # assert not op.exists(test_uncompress_file)
        # ok with pwd
        r_uncompress = z7.uncompress(test_compress_file, test_out_dir, pwd=pwd)
        assert r_uncompress[0] == "ok"
        assert op.exists(test_uncompress_file)
        assert filecmp.cmp(test_file, test_uncompress_file) is True
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)

    def test_compress_dir(self):
        tmp_path = get_tmp_path()
        test_dir = op.join(tmp_path, "test")
        test_dir_file = op.join(test_dir, "test.txt")
        test_out_dir = op.join(tmp_path, "out")
        test_compress_file = op.join(tmp_path, "test.7z")
        test_uncompress_dir = op.join(test_out_dir, "test")
        test_uncompress_dir_file = op.join(test_uncompress_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)
        z7 = Zip7Mix()
        r_compress = z7.compress(test_dir)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = z7.uncompress(test_compress_file, test_out_dir)
        assert r_uncompress[0] == "ok"
        assert op.exists(test_uncompress_dir)
        assert op.exists(test_uncompress_dir_file)
        assert filecmp.cmp(test_dir_file, test_uncompress_dir_file) is True
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)

    def test_mix(self):
        tmp_path = get_tmp_path()
        test_file = op.join(tmp_path, "test.txt")
        test_out_dir = op.join(tmp_path, "out")
        test_compress_file = op.join(tmp_path, "test.txt.7z")
        test_uncompress_file = op.join(test_out_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)
        z7mix = Zip7Mix()
        r_compress = z7mix.mix(test_file)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = z7mix.unmix(test_compress_file, test_out_dir)
        assert r_uncompress[0] == "ok"
        assert op.exists(test_uncompress_file)
        assert filecmp.cmp(test_file, test_uncompress_file) is True
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)

    def test_mix_dir(self):
        tmp_path = get_tmp_path()
        test_dir = op.join(tmp_path, "test")
        test_dir_file = op.join(test_dir, "test.txt")
        test_out_dir = op.join(tmp_path, "out")
        test_compress_file = op.join(tmp_path, "test.7z")
        test_uncompress_dir = op.join(test_out_dir, "test")
        test_uncompress_dir_file = op.join(test_uncompress_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)
        z7mix = Zip7Mix()
        r_compress = z7mix.mix(test_dir)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = z7mix.unmix(test_compress_file, test_out_dir)
        assert r_uncompress[0] == "ok"
        assert op.exists(test_uncompress_dir)
        assert op.exists(test_uncompress_dir_file)
        assert filecmp.cmp(test_dir_file, test_uncompress_dir_file) is True
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)
    
