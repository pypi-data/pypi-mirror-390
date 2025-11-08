import re
from getpass import getpass
from .str_to_list import encrypt_str_to_list
from .str_to_list import decrypt_list_to_str

def get_prompts_line(s, pattern=r"prompts\((\d+)\)"):
    match = re.search(pattern, s)
    if match:
        return int(match[1])

def str_from_txtfile(fin) -> str:
    with open(fin, encoding="utf-8") as f:
        s = f.read()
    return s


def str_to_txtfile(s: str, fout=None):
    if fout is None:
        print(s)
    else:
        with open(fout, "w", encoding="utf-8") as f:
            f.write(s)

def encrypt_txtfile(fin, fout=None, password=None, prompt='prompts(1)'):
    s = str_from_txtfile(fin)

    if not prompt:
        prompt = input("input prompt=")

    if password == "[input]":
        password = getpass("input password=")

    if password:
        encrypted_list = encrypt_str_to_list(s, password)
        encrypted_list[0] = "-"
    else:
        encrypted_list = encrypt_str_to_list(s)

    s2 = "\n".join([prompt] + encrypted_list)

    if fout == ".":
        fout = fin+"_1"
        
    str_to_txtfile(s2, fout)


def decrypt_txtfile(fin, fout=None, password=None):
    s = str_from_txtfile(fin)
    if password == "[input]":
        password = getpass("input password=")
    s_list = s.split("\n")
    prompts = get_prompts_line(s_list[0])
    if prompts is None:
        prompts_line = 1
    else:
        prompts_line = prompts
    encrypted_list = s_list[prompts_line:]

    if encrypted_list[0] == "-" and password is None:
        password = getpass("input password=")

    if password is None:
        s2 = decrypt_list_to_str(encrypted_list)
    else:
        s2 = decrypt_list_to_str(encrypted_list, password)
        
    if fout == ".":
        fout = fin+"_2"
    str_to_txtfile(s2, fout)

