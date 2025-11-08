def int_bytes_length(n: int) -> int:
    if n == 0:
        return 1
    bits = n.bit_length()
    bytes_needed = (bits + 7) // 8
    return max(bytes_needed, 1)


def int_to_bytes(n: int, length=1) -> bytes:
    return n.to_bytes(length, byteorder="big")


def int_from_bytes(intbs: bytes) -> int:
    return int.from_bytes(intbs, byteorder="big")
