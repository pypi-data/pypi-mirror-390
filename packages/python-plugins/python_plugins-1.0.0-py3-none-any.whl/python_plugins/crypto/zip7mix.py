import os
import os.path as op
from pathlib import Path
import hashlib
import subprocess
from .mixbyte import MixByte


class Zip7Mix(MixByte):
    def __init__(self, zipcmd="7z"):
        self.zipcmd = zipcmd
        self.z7_available = self.check_7z_available()

    def check_7z_available(self) -> bool:
        try:
            subprocess.run([self.zipcmd], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def compress(self, file_or_dir, archive_path=None, pwd=None, silent=True):
        path_obj = Path(file_or_dir)
        if not path_obj.exists():
            raise

        if archive_path is None:
            archive_path = file_or_dir + ".7z"

        cmd = [self.zipcmd, "a"]
        if silent:
            cmd.append("-bso0")
        if pwd:
            cmd.extend([f"-p{pwd}", "-mhe=on"])
        cmd.extend([archive_path, file_or_dir])

        try:
            subprocess.run(cmd, check=True)
            return ("ok", archive_path)
        except subprocess.CalledProcessError as e:
            return ("fail", f"{e}")

    def list_archive(self, archive_path, pwd=None, silent=True):
        cmd = [self.zipcmd, "l"]
        if silent:
            cmd.append("-bso0")
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.append(archive_path)

        try:
            subprocess.run(cmd, check=True)
            return ("ok", archive_path)
        except subprocess.CalledProcessError as e:
            return ("fail", f"{e}")

    def uncompress(
        self,
        archive_path,
        output_path=None,
        pwd=None,
        overwrite: bool = True,
        silent=True,
    ):
        archive_obj = Path(archive_path)

        if output_path is None:
            output_dir = archive_obj.parent
        else:
            output_dir = Path(output_path)

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if not output_dir.is_dir():
            return ("fail", f"{output_dir} is not dir")

        cmd = [self.zipcmd, "x", "-y"]
        if silent:
            cmd.append("-bso0")
        if not overwrite:
            cmd.append("-aos")
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.extend([archive_path, f"-o{output_dir}"])

        try:
            subprocess.run(cmd, check=True)
            return ("ok", f"{output_dir}")
        except subprocess.CalledProcessError as e:
            return ("fail", f"{e}")

    def mix(self, file_or_dir, archive_path=None):
        pwd = self.generate_password(64)
        r_compress = self.compress(file_or_dir, archive_path=archive_path, pwd=pwd)
        if r_compress[0] != "ok":
            return r_compress
        archive_path = r_compress[1]
        with open(archive_path, "rb") as f:
            data = f.read()
        blocks = [
            {"name": "hash", "body": self.create_hash_block(data)},
            {"name": "pwd", "body": self.create_pwd_block(pwd.encode("utf-8"))},
        ]
        tail_bytes = self.build_tail_link_blocks(blocks)
        with open(archive_path, "ab") as f:
            f.write(tail_bytes)
        return ("ok", archive_path)

    def unmix(self, archive_path, output_path=None):
        file_size = op.getsize(archive_path)
        with open(archive_path, "rb") as f:
            if file_size > 1000:
                f.seek(-1000, os.SEEK_END)
            data = f.read()
        parse_result = self.parse_tail_link_blocks(data)
        pwd = parse_result["pwd"].decode("utf-8")
        with open(archive_path, "rb") as f:
            data = f.read(file_size - parse_result["block_size"])
        if "hash" in parse_result and (
            parse_result["hash"][1]
            != getattr(hashlib, parse_result["hash"][0])(data).digest()
        ):
            raise Exception("hash not match")

        result = self.uncompress(
            archive_path=archive_path, output_path=output_path, pwd=pwd
        )
        return result
