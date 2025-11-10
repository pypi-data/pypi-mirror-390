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
from dexdata.dataset import DATASET_BASE_PATH


__version__ = "0.0.2"

BASE_PATH = os.path.join(DATASET_BASE_PATH, ".shadow")
_VERSIONED_PATH = os.path.join(BASE_PATH, "v1")
NAS_BASE_URL = ""


cfg = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "configs",
    "cfg.json",
)


with open(cfg, "r", encoding="utf-8") as f:
    cfg_data = json.load(f)
    NAS_BASE_URL = cfg_data.get("shadow").get("base_url")


def __get(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            response.raise_for_status()
    except requests.RequestException as e:
        pass
    else:
        return response


def __download_file(url, save_path):
    response = __get(url)
    if not response:
        return
    save_path = urllib.parse.unquote(save_path)
    os.makedirs(save_path, exist_ok=True)
    filepath = os.path.join(save_path, os.path.basename(url))
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                break
            f.write(chunk)


def __download(url, save_path):
    response = __get(url)
    if not response:
        return
    content_type = response.headers.get("Content-Type") or response.headers.get(
        "content-type"
    )
    if "text/html" in content_type and re.search(
        r"<title>Index of .*?</title>", response.text
    ):
        # 表示这是一个目录
        url = url if url.endswith("/") else f"{url}/"
        save_path = os.path.join(save_path, url.split("/")[-2])
        for match in re.finditer(r"<a href=\"(?P<link>.*?)\">", response.text):
            link = match.groupdict()["link"]
            if link == "../":
                continue
            child_url = urllib.parse.urljoin(url, link)
            if link.endswith("/"):
                if not urllib.parse.urlparse(url).path.startswith(link):
                    # 目录，需要递归搜索
                    __download(child_url, save_path)
            else:
                # 文件
                __download_file(child_url, save_path)
    else:
        __download_file(url, save_path)


def get_data_project(data_project_name: str, target_dir: str = None) -> str:
    """
    根据项目名称从NAS获取对应的影子模式数据集并保存到指定的本地路径
    :param data_project_name: NAS上影子模式数据集名称
    :param target_dir: 本地保存路径，若使用默认参数值则保存在$HOME/dexdata/ds/.shadow/v1/路径下面
    :return: 保存到本地的路径
    """
    nas_url = NAS_BASE_URL + data_project_name
    if target_dir is None:
        target_dir = _VERSIONED_PATH

    local_path = os.path.join(target_dir, data_project_name)
    if not os.path.exists(local_path):
        __download(nas_url, target_dir)
    return local_path


def load_project_names() -> List[dict]:
    """
    列举NAS上所有影子模式数据的项目名称和数据集类型
    :return: 项目名称和数据集类型字典列表
    """
    url = NAS_BASE_URL
    result = []
    proj_names = []
    response = __get(url)
    if not response:
        return result
    content_type = response.headers.get("Content-Type") or response.headers.get(
        "content-type"
    )
    if "text/html" in content_type and re.search(
        r"<title>Index of .*?</title>", response.text
    ):
        # 表示这是一个目录
        for match in re.finditer(r"<a href=\"(?P<link>.*?)\">", response.text):
            link = match.groupdict()["link"]
            if link == "../":
                continue
            pure_link = link if not link.endswith("/") else link[:-1]
            data_proj_name = urllib.parse.unquote(pure_link)
            proj_names.append(data_proj_name)

    for name in proj_names:
        item = {}
        type = "raw"
        if name.startswith("shadow-benchmark-"):
            type = "prepared"
        item[name] = {"type": type}
        result.append(item)

    return result
