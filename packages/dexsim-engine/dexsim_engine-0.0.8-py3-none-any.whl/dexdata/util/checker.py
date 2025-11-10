# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os
import hashlib
import glob
from typing import List


size_dict = {}
md5_dict = {}


def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_size(file_path):
    file_size = os.path.getsize(file_path)
    return file_size


def get_size_dict(size_file_path, pattern="obj"):
    global size_dict
    with open(size_file_path, mode="r", encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if pattern in line:
                file_name = line.split(":")[0]
                size = int(line.split(":")[-1].strip())
                size_dict[file_name] = size


def get_md5_dict(md5_file_path, pattern="obj"):
    global md5_dict
    with open(md5_file_path, mode="r", encoding="utf-8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if pattern in line:
                file_name = line.split(":")[0]
                md5 = line.split(":")[-1].strip()
                md5_dict[file_name] = md5


def check_file(file_path):
    is_ok = True
    file_md5 = get_md5(file_path)
    file_size = get_size(file_path)
    file_name = file_path.split(os.sep)[-1]
    if file_name in size_dict.keys():
        if file_size != size_dict.get(file_name):
            is_ok = False
    else:
        is_ok = False

    if file_name in md5_dict.keys():
        if file_md5 != md5_dict.get(file_name):
            is_ok = False
    else:
        is_ok = False

    return is_ok


def parse_dir(path_dir: str, extend=".7z") -> List[str]:
    target_pattern = os.path.join(path_dir, "**", "*" + extend)
    file_list = glob.glob(target_pattern, recursive=True)
    return file_list


if __name__ == "__main__":
    md5_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "md5.yml",
    )
    size_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "size.yml",
    )
    get_md5_dict(md5_file_path)
    get_size_dict(size_file_path)

    target_dir = "D:\\ABC\\test3"
    all_7zs = parse_dir(target_dir, ".7z")
    count = len(all_7zs)
    index = 1
    for file in all_7zs:
        file_name = file.split(os.sep)[-1]
        print(f"[{str(index)}/{str(count)}] Checking file: {file_name}")
        is_ok = check_file(file)
        if is_ok is False:
            print(f"{file_name}--->{is_ok}")
        index = index + 1
