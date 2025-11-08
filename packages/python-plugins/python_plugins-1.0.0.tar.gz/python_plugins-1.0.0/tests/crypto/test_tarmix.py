import pytest
import os
import os.path as op
import shutil
import filecmp
from python_plugins.crypto.tarmix import TarMix


def get_tmp_path():
    parent_dir = op.realpath(op.dirname(__file__))
    tmp_path = op.realpath(op.join(parent_dir, "..", "tmp"))
    return tmp_path

class TestTarMix:

    def test_compress(self):
        tmp_path = get_tmp_path()
        test_file = op.join(tmp_path, "test.txt")
        test_out_dir = op.join(tmp_path, "out")
        test_compress_file = op.join(tmp_path, "test.txt.tar.gz")
        test_uncompress_file = op.join(test_out_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)
        tarmix = TarMix()
        r_compress = tarmix.compress(test_file)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = tarmix.uncompress(test_compress_file, test_out_dir)
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
        test_compress_file = op.join(tmp_path, "test.tar.gz")
        test_uncompress_dir = op.join(test_out_dir, "test")
        test_uncompress_dir_file = op.join(test_uncompress_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)
        tarmix = TarMix()
        r_compress = tarmix.compress(test_dir)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = tarmix.uncompress(test_compress_file, test_out_dir)
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
        test_compress_file = op.join(tmp_path, "test.txt.tar.gz")
        test_uncompress_file = op.join(test_out_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_file):
            os.unlink(test_uncompress_file)
        tarmix = TarMix()
        r_compress = tarmix.mix(test_file)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = tarmix.unmix(test_compress_file, test_out_dir)
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
        test_compress_file = op.join(tmp_path, "test.tar.gz")
        test_uncompress_dir = op.join(test_out_dir, "test")
        test_uncompress_dir_file = op.join(test_uncompress_dir, "test.txt")
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)
        tarmix = TarMix()
        r_compress = tarmix.mix(test_dir)
        assert len(r_compress) == 2
        assert r_compress[0] == "ok"
        assert test_compress_file == r_compress[1]
        assert op.exists(test_compress_file)
        r_uncompress = tarmix.unmix(test_compress_file, test_out_dir)
        assert r_uncompress[0] == "ok"
        assert op.exists(test_uncompress_dir)
        assert op.exists(test_uncompress_dir_file)
        assert filecmp.cmp(test_dir_file, test_uncompress_dir_file) is True
        if os.path.exists(test_compress_file):
            os.unlink(test_compress_file)
        if os.path.exists(test_uncompress_dir):
            shutil.rmtree(test_uncompress_dir)
    



