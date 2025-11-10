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
from dexdata.resource.d3model import D3MODEL_BASE_PATH


__version__ = "0.0.1"

BASE_PATH = os.path.join(D3MODEL_BASE_PATH, ".cad")
_VERSIONED_PATH = os.path.join(BASE_PATH, "v1")
minio_client = None
bucket_name = ""


cfg = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "configs",
    "cfg.json",
)


if minio_client is None:
    with open(cfg, "r", encoding="utf-8") as f:
        cfg_data = json.load(f)
    bucket_name = cfg_data.get("cad").get("bucket")
    endpoint = cfg_data.get("minio").get("endpoint")
    access_key = cfg_data.get("minio").get("access_key")
    secret_key = cfg_data.get("minio").get("secret_key")
    minio_client = Minio(endpoint, access_key, secret_key, secure=False)


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
    prefix_exists = False
    for obj in objects:
        prefix_exists = True
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
    if not prefix_exists:
        raise Exception(f"桶{bucket}中不存在前缀{prefix}")
    return os.path.join(save_path, prefix)


def load_cad_names() -> List[str]:
    """
    列举所有CAD名称
    :return: CAD名称列表
    """
    global minio_client, bucket_name
    result = set()
    try:
        objects = minio_client.list_objects(bucket_name, prefix="", recursive=True)
        for obj in objects:
            if "/" in obj.object_name:
                root_prefix = obj.object_name.split("/")[0]
                result.add(root_prefix)

        return list(result)
    except Exception as ex:
        return []


def load_cad(cad_name: str, save_path: str = None) -> str:
    """
    根据CAD名称获取对应的CAD并保存到指定的本地路径
    :param cad_name: CAD名称
    :param save_path: 本地保存路径，若使用默认参数值则保存在$HOME/dexdata/rs/d3model/.cad/v1/路径下面
    :return: 保存到本地的路径
    """
    global minio_client, bucket_name

    if save_path is None:
        save_path = _VERSIONED_PATH

    prefix = cad_name if cad_name.endswith("/") else cad_name + "/"
    local_path = os.path.join(save_path, cad_name)
    if not os.path.exists(local_path):
        __download_objects_under_prefix(
            minio_client=minio_client,
            bucket=bucket_name,
            prefix=prefix,
            save_path=save_path,
        )
    return local_path
