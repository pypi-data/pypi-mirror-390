# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os
import json
import requests
import re
import urllib.parse
from typing import List
from minio import Minio
from dexdata.dataset import DATASET_BASE_PATH
from dexdata.util.nas_downloader import download


__version__ = "0.0.1"

BASE_PATH = os.path.join(DATASET_BASE_PATH, ".standard")
_VERSIONED_PATH = os.path.join(BASE_PATH, "v1")
minio_client = None
bucket_name = ""
type_info_object = "type_info.json"
# 互联网根URL
INTERNET_ROOT_URL = ""

cfg = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "configs",
    "cfg.json",
)


if minio_client is None:
    with open(cfg, "r", encoding="utf-8") as f:
        cfg_data = json.load(f)
    bucket_name = cfg_data.get("standard").get("bucket")
    endpoint = cfg_data.get("minio").get("endpoint")
    access_key = cfg_data.get("minio").get("access_key")
    secret_key = cfg_data.get("minio").get("secret_key")
    minio_client = Minio(endpoint, access_key, secret_key, secure=False)
    INTERNET_ROOT_URL = cfg_data.get("standard").get("internet")


def __download_objects_under_prefix(
    minio_client: Minio, bucket: str, prefix: str, save_path: str
):
    """
    下载指定bucket中指定前缀下的所有object
    :param minio_client: minio客户端对象
    :param bucket: 存储桶名称
    :param prefix: 前缀名(以"/"结尾)
    :param save_path:保存在本地的根路径
    :return: 无
    """
    objects = minio_client.list_objects(bucket, prefix=prefix, recursive=True)
    for obj in objects:
        data = minio_client.get_object(bucket, obj.object_name)
        # print(f'object_name: {obj.object_name}')
        file_path = os.path.join(save_path, obj.object_name)
        target_file_path = file_path.replace("/", os.path.sep)
        # print(f'target_file_path: {target_file_path}')
        parent_dir = os.path.dirname(target_file_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(target_file_path, "wb") as file_data:
            for d in data.stream(32 * 1024):
                file_data.write(d)
    return os.path.join(save_path, prefix)


def load_project_names() -> List[dict]:
    """
    列举所有standard数据的项目名称和数据集类型
    :return: 项目名称和数据集类型字典列表
    """
    global minio_client, bucket_name, type_info_object

    try:
        response = minio_client.get_object(bucket_name, type_info_object)
        type_info_str = response.data.decode("utf-8")
        type_info_dict = json.loads(type_info_str)
        name_list = []
        for key in type_info_dict.keys():
            item = {}
            item[key] = {"type": type_info_dict[key]}
            name_list.append(item)
        return name_list
    except Exception as ex:
        return []
    finally:
        response.close()
        response.release_conn()


def get_data_project(data_project_name: str, target_dir: str = None) -> str:
    """
    根据项目名称获取对应的数据集并保存到指定的本地路径
    :param data_project_name: 数据集名称
    :param target_dir: 本地保存路径，若使用默认参数值则保存在$HOME/dexdata/ds/.standard/v1/路径下面
    :return: 保存到本地的路径
    """
    global minio_client, bucket_name, INTERNET_ROOT_URL

    if target_dir is None:
        target_dir = _VERSIONED_PATH

    prefix = (
        data_project_name
        if data_project_name.endswith("/")
        else data_project_name + "/"
    )
    local_path = os.path.join(target_dir, data_project_name)
    if not os.path.exists(local_path):  # 本地不存在该数据集目录时才会下载，否则直接跳过
        try:
            __download_objects_under_prefix(
                minio_client=minio_client,
                bucket=bucket_name,
                prefix=prefix,
                save_path=target_dir,
            )
        except Exception as ex:
            internet_target_url = INTERNET_ROOT_URL + prefix
            download(internet_target_url, target_dir)

        return local_path
