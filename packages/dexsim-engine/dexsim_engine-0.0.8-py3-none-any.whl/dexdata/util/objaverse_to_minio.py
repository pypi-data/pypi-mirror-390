# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os
import json
import glob
import sys
import gzip
from typing import Dict
from minio_helper import MinIOHelper
from multiprocessing import Process


objaverse_minio_conf = {
    "endpoint": "192.168.3.43:9009",
    "access_key": "dexdata",
    "secret_key": "dexdata123.",
    "secure": False,
    "bucket_name": "dex-rs-model-obj",
}


def pick_parse_object_data(object_path: str):
    """
    将objaverse数据集中原始的object-paths.json中的000-019的相关数据单独提取出来并保存到.gz文件
    :param object_path: object-paths.json文件绝对路径
    :return: 是否成功
    """
    cur_dir = os.path.dirname(object_path)
    with open(object_path, mode="r", encoding="utf-8") as f:
        data_dict = json.load(f)
    result_data = {}
    for key in data_dict.keys():
        value = data_dict[key]
        sub_name = value.split("/")[1]  # 000-023
        index = sub_name.split("-")[-1]
        index_num = int(index)
        if index_num <= 19:
            result_data[key] = value
    result_data_str = json.dumps(result_data)
    result_file_path = os.path.join(cur_dir, "object-paths.json.gz")
    with gzip.open(result_file_path, "wb") as f:
        f.write(result_data_str.encode("utf-8"))


def push_metadata_to_minio(dir_path: str) -> Dict[str, str]:
    pattern = os.path.join(dir_path, f"**{os.path.sep}*" + ".gz")
    path_list = []
    for file in glob.glob(pattern, recursive=True):
        path_list.append(file)
    minio_helper = MinIOHelper(**objaverse_minio_conf)
    result_dict = {}
    for file in path_list:
        file_path, url = minio_helper.upload_data_without_tag(file, "application/gz")
        result_dict[file_path] = url
    return result_dict


def push_glb_data_to_minio_out(dir_path: str):
    subdirs = []
    for root, dirs, files in os.walk(dir_path):
        for d in dirs:
            subdirs.append(os.path.join(root, d))
    p_list = []
    for sub_dir in subdirs:
        p = Process(target=push_glb_data_to_minio, kwargs={"sub_dir_path": sub_dir})
        p_list.append(p)
        p.start()
    for p1 in p_list:
        p1.join()


def push_glb_data_to_minio(sub_dir_path: str):

    pattern = os.path.join(sub_dir_path, f"**{os.path.sep}*" + ".glb")
    path_list = []
    for file in glob.glob(pattern, recursive=True):
        path_list.append(file)
    minio_helper = MinIOHelper(**objaverse_minio_conf)

    parent_dir = (
        os.path.dirname(sub_dir_path)
        if not sub_dir_path.endswith(os.sep)
        else os.path.dirname(sub_dir_path[:-1])
    )
    sub_dir_name = (
        sub_dir_path.split(os.sep)[-1]
        if not sub_dir_path.endswith(os.sep)
        else sub_dir_path.split(os.sep)[-2]
    )
    log_file_path = os.path.join(parent_dir, sub_dir_name + "-object-paths.json")
    result_dict = {}
    for file in path_list:
        file_path, url = minio_helper.upload_data_with_self_name(
            file, "application/glb"
        )
        file_name = file.split(os.sep)[-1]
        file_name_without_ext = file_name.split(".glb")[0]
        result_dict[file_name_without_ext] = url
    with open(log_file_path, mode="w", encoding="utf-8") as f:
        json.dump(result_dict, f)


if __name__ == "__main__":
    print("begin...")
    # object_path = 'C:\\Users\\Administrator\\Downloads\\object-paths.json\\object-paths.json'
    # pick_parse_object_data(object_path)
    glb_data_dir = sys.argv[1]
