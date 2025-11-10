# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import glob
import os
import argparse
import time
import py7zr
import shutil
import json
from typing import List
from minio_helper import minio_conf, MinIOHelper


target_7z_dir = None


def unzip_7z(path_7z: str) -> str:
    global target_7z_dir
    result_path = path_7z.split(".7z")[0]
    with py7zr.SevenZipFile(path_7z, mode="r") as z:
        z.extractall(path=result_path)
    target_7z_dir = result_path
    return result_path


def parse_7z(path_7z: str, extend=".obj") -> List[str]:
    target_path = unzip_7z(path_7z)
    target_path = target_path[:-1] if target_path.endswith(os.path.sep) else target_path
    pattern = os.path.join(target_path, f"**{os.path.sep}*" + extend)
    path_list = []
    for file in glob.glob(pattern, recursive=True):
        path_list.append(file)
    return path_list


def parse_dir(path_dir: str, extend=".7z") -> List[str]:
    target_pattern = os.path.join(path_dir, "**", "*" + extend)
    file_list = glob.glob(target_pattern, recursive=True)
    return file_list


if __name__ == "__main__":
    print("begin...")

    # parser = argparse.ArgumentParser(
    #     description='Parse all the target files under the given directory.'
    # )
    #
    # parser.add_argument(
    #     '--abs_dir', type=str, required=True, default="",
    #     help='the absolute path of target files directory'
    # )
    #
    # args = parser.parse_args()
    #
    # target_dir = args.abs_dir
    minio_helper = MinIOHelper(**minio_conf)

    target_dir = "D:\\ABC\\test3"
    zip_file_list = parse_dir(target_dir, ".7z")
    obj_file_abs_path_list = []
    total_uid_objs_dict = {}
    # 采样，共大约10W个文件
    total = 100000
    zip_file_count = len(zip_file_list)
    each_zip_obj_count = total // zip_file_count
    json_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    zip_index = 1
    for file in zip_file_list:
        print(
            f"{str(zip_index)}/{str(zip_file_count)} {file} Begin to write to MinIO..."
        )
        abc_obj_path_dic = {}
        zip_file_name = file.split(os.sep)[-1]
        obj_file_abs_path = parse_7z(file, ".obj")
        obj_file_abs_path_list.extend(obj_file_abs_path)
        obj_count = len(obj_file_abs_path)
        interval = obj_count // each_zip_obj_count
        index = 1
        sampled_obj_file_list = obj_file_abs_path[::interval]
        sampled_count = len(sampled_obj_file_list)
        for obj_file_path in sampled_obj_file_list:
            uid, url = minio_helper.upload_data_with_auto_generated_uid(
                obj_file_path, "application/binary"
            )
            print(f"{str(index)}/{str(sampled_count)}: {uid} ---> {url}")
            abc_obj_path_dic[uid] = url
            index = index + 1
        print(f"Delete 7z directory: {target_7z_dir}")
        shutil.rmtree(target_7z_dir)

        with open(os.path.join(json_dir, zip_file_name + ".json"), "w") as f:
            json.dump(abc_obj_path_dic, f)

        total_uid_objs_dict.update(abc_obj_path_dic)
        zip_index = zip_index + 1

    with open(os.path.join(json_dir, "total_uid_objs_dict.json"), "w") as f:
        json.dump(total_uid_objs_dict, f)

    total_count = len(total_uid_objs_dict.keys())
    print(f"total_uid_objs_dict:{str(total_count)}")
    # print(obj_file_abs_path_list)
    # print(len(obj_file_abs_path_list))
    # print(abc_obj_paths)
    # print(len(abc_obj_paths.keys()))
