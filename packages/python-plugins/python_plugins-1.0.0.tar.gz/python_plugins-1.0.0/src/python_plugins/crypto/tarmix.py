import os
import os.path as op
import io
import hashlib
from pathlib import Path
import tarfile
from .mixbyte import MixByte
from .cipher import AesCipher


class TarMix(MixByte):
    def __init__(self):
        pass

    def compress(self, file_or_dir, archive_path=None):
        path_obj = Path(file_or_dir)
        if not path_obj.exists():
            raise

        if archive_path is None:
            archive_path = file_or_dir + ".tar.gz"

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(file_or_dir, arcname=op.basename(file_or_dir))

        return ("ok", archive_path)

    def uncompress(self, archive_path, output_path=None):
        archive_obj = Path(archive_path)

        if output_path is None:
            output_dir = archive_obj.parent
        else:
            output_dir = Path(output_path)

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if not output_dir.is_dir():
            return ("fail", f"{output_dir} is not dir")

        output_path = f"{output_dir}"
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(path=output_path, filter="data")

        return ("ok", output_path)

    def mix(self, file_or_dir, archive_path=None):
        path_obj = Path(file_or_dir)
        if not path_obj.exists():
            raise

        if archive_path is None:
            archive_path = file_or_dir + ".tar.gz"
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            tar.add(file_or_dir, arcname=op.basename(file_or_dir))

        tar_data = tar_buffer.getvalue()
        cipher = AesCipher()
        cipher.generate_key()
        cipher.generate_cipher()
        encryptor = cipher.create_encryptor()
        crypt_data = encryptor.update(cipher.pad(tar_data)) + encryptor.finalize()
        pwd = cipher.key + cipher.iv
        blocks = [
            {"name": "hash", "body": self.create_hash_block(crypt_data)},
            {"name": "pwd", "body": self.create_pwd_block(pwd)},
        ]
        tail_bytes = self.build_tail_link_blocks(blocks)
        with open(archive_path, "wb") as f:
            f.write(crypt_data)
            f.write(tail_bytes)

        return ("ok", archive_path)

    def unmix(self, archive_path, output_path=None):
        archive_obj = Path(archive_path)

        if output_path is None:
            output_dir = archive_obj.parent
        else:
            output_dir = Path(output_path)

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if not output_dir.is_dir():
            return ("fail", f"{output_dir} is not dir")

        output_path = f"{output_dir}"

        file_size = op.getsize(archive_path)
        with open(archive_path, "rb") as f:
            if file_size > 1000:
                f.seek(-1000, os.SEEK_END)
            data = f.read()
        parse_result = self.parse_tail_link_blocks(data)
        pwd = parse_result["pwd"]

        with open(archive_path, "rb") as f:
            data = f.read(file_size - parse_result["block_size"])
        if "hash" in parse_result and (
            parse_result["hash"][1]
            != getattr(hashlib, parse_result["hash"][0])(data).digest()
        ):
            raise Exception("hash not match")

        crypt_data = data
        cipher = AesCipher(pwd[:32], pwd[32:])
        cipher.generate_cipher()
        decryptor = cipher.create_decryptor()
        uncrypt_data = decryptor.update(crypt_data) + decryptor.finalize()
        tar_data = cipher.unpad(uncrypt_data)
        tar_buffer = io.BytesIO(tar_data)
        with tarfile.open(fileobj=tar_buffer, mode="r:gz") as tf:
            tf.extractall(path=output_path, filter="data")

        return ("ok", output_path)
