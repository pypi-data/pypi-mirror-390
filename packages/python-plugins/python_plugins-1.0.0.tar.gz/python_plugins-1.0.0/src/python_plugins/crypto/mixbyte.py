import os
import os.path as op
import hashlib
import random
from enum import Enum

from .utils import int_bytes_length, int_to_bytes, int_from_bytes


class BlockName(Enum):
    MSG = "msg"
    HASH = "hash"
    PWD = "pwd"
    UNKNOWN = "unknown"
    END = "end"


class BlockCategory(Enum):
    MSG = 0
    HASH = 1
    PWD = 2
    UNKNOWN = 254
    END = 255


class MixByte:
    @staticmethod
    def generate_password(n: int = 32) -> str:
        return hashlib.sha256(os.urandom(10)).hexdigest()[:n]

    def int_to_nbytes(self, n: int) -> bytes:
        length = int_bytes_length(n)
        length_byte = int_to_bytes(length)
        nbytes = int_to_bytes(n, length)
        return (length_byte, nbytes)

    def create_mix_tag(self):
        return b"MIX" + os.urandom(3) + b"\x00\x00"

    def check_mix_tag(self, data: bytes):
        return data[:3] + data[-2:] == b"MIX\x00\x00"

    def create_hash_block(self, data: bytes, hash_method="md5"):
        return (
            hash_method.encode("utf-8")
            + b"#"
            + getattr(hashlib, hash_method)(data).digest()
        )

    def parse_hash_block(self, data):
        (hash_method_bytes, hash_body) = data.split(b"#", 1)
        return hash_method_bytes.decode("utf-8"), hash_body

    def create_pwd_block(self, pwd: bytes):
        if (n_pwd := len(pwd)) == 0:
            raise Exception("n_pwd == 0!")
        if n_pwd > 128:
            raise Exception("n_pwd > 128!")

        n_block = min(2 * n_pwd, 128)
        data = os.urandom(n_block * 2)
        data_list = list(data)
        pos_list = random.sample(range(n_block - 1), n_pwd - 1)

        # start fixed at end
        curr_pos = -2
        for i, pos in enumerate(pos_list):
            data_list[curr_pos] = pwd[i]
            next_pos = pos * 2
            data_list[curr_pos + 1] = next_pos
            curr_pos = next_pos

        data_list[curr_pos] = pwd[-1]
        data_list[curr_pos + 1] = 255

        return bytes(data_list)

    def parse_pwd_block(self, data: bytes):
        pwd_list = []
        curr_pos = -2
        while curr_pos != 255:
            pwd_list.append(data[curr_pos])
            curr_pos = data[curr_pos + 1]
        return bytes(pwd_list)

    def build_tail_link_blocks(self, blocks: list[dict]) -> bytes:
        parts = [BlockCategory.END.value.to_bytes()]

        for block in blocks:
            parts.append(block["body"])
            (length_byte, nbytes) = self.int_to_nbytes(len(block["body"]))
            parts.extend([nbytes, length_byte])
            match block["name"]:
                case BlockName.HASH.value:
                    parts.append(BlockCategory.HASH.value.to_bytes())
                case BlockName.PWD.value:
                    parts.append(BlockCategory.PWD.value.to_bytes())

        parts.append(self.create_mix_tag())

        return b"".join(parts)

    def parse_tail_link_blocks(self, data):
        data_length = len(data)
        if not self.check_mix_tag(data[-8:]):
            return None
        result = {}
        curr_pos = -9
        while data[curr_pos] != BlockCategory.END.value:
            category = data[curr_pos]
            nlength = data[curr_pos - 1]
            block_size = int_from_bytes(data[curr_pos - 1 - nlength : curr_pos - 1])
            block = data[curr_pos - 1 - nlength - block_size : curr_pos - 1 - nlength]
            match category:
                case BlockCategory.MSG.value:
                    result[BlockName.MSG.value] = block
                case BlockCategory.HASH.value:
                    result[BlockName.HASH.value] = self.parse_hash_block(block)
                case BlockCategory.PWD.value:
                    result[BlockName.PWD.value] = self.parse_pwd_block(block)
                case BlockCategory.UNKNOWN.value:
                    result[BlockName.UNKNOWN.value] = block
                case BlockCategory.END.value:
                    result[BlockName.END.value] = block
                case _:
                    raise Exception("category not match!")
            curr_pos = curr_pos - 1 - nlength - block_size - 1
            if curr_pos < -data_length:
                raise Exception("exceed max size!")
        result["block_size"] = -curr_pos
        return result

    def list_archive_mix(self, archive_path):
        file_size = op.getsize(archive_path)
        with open(archive_path, "rb") as f:
            if file_size > 1000:
                f.seek(-1000, os.SEEK_END)
            data = f.read()
        result = self.parse_tail_link_blocks(data)
        return result

    def mix_bytes_to_binary(self, data, insert_bytes):
        n_data = len(data)
        n_insert = len(insert_bytes)
        pos_list = sorted(random.sample(range(n_data), n_insert))
        parts = []
        pre_pos = 0

        for i, curr_pos in enumerate(pos_list):
            parts.append(data[pre_pos:curr_pos])
            parts.append(insert_bytes[i : i + 1])
            if i < n_insert - 1:
                parts.extend(list(self.int_to_nbytes(pos_list[i + 1])))
            else:
                parts.extend(list(self.int_to_nbytes(0)))
            pre_pos = curr_pos

        parts.append(data[pre_pos:])
        return (b"".join(parts), pos_list[0])

    def extract_from_mixed_binary(self, data, start_pos):
        pos_list = [start_pos]
        part_begin_pos = 0
        part_end_pos = start_pos
        parts = [data[part_begin_pos:part_end_pos]]
        insert_parts = [data[part_end_pos]]
        next_pos_size = data[part_end_pos + 1]
        next_pos = int_from_bytes(
            data[part_end_pos + 2 : part_end_pos + 2 + next_pos_size]
        )

        while next_pos > 0:
            pos_list.append(next_pos)
            part_begin_pos = part_end_pos + 2 + next_pos_size
            part_end_pos = part_begin_pos + pos_list[-1] - pos_list[-2]
            parts.append(data[part_begin_pos:part_end_pos])
            insert_parts.append(data[part_end_pos])
            next_pos_size = data[part_end_pos + 1]
            next_pos = int_from_bytes(
                data[part_end_pos + 2 : part_end_pos + 2 + next_pos_size]
            )

        parts.append(data[part_end_pos + 2 + next_pos_size :])
        new_data = b"".join(parts)
        insert_bytes = bytes(insert_parts)
        result = {"data": new_data, "insert": insert_bytes}
        return result
