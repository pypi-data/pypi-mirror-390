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
from dexdata.util.utils import remove_directory
from dexdata.dataset import DATASET_BASE_PATH


__version__ = "0.0.1"

BASE_PATH = os.path.join(DATASET_BASE_PATH, ".stereo")
_VERSIONED_PATH = os.path.join(BASE_PATH, "v1")
NAS_BASE_URL = ""


cfg = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "configs",
    "cfg.json",
)


with open(cfg, "r", encoding="utf-8") as f:
    cfg_data = json.load(f)
    NAS_BASE_URL = cfg_data.get("stereo").get("base_url")


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


def __download(url, save_path, keep_url_dir=True):
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
        if keep_url_dir:
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


def get_all_data_projects(overwrite: bool, save_path: str = None) -> List[str]:
    """
    从NAS获取所有数据集并保存到指定的本地路径，同时根据overwrite的值决定覆盖本地已有同名数据集还是跳过下载
    :param overwrite: 当本地目录下已经存在同名数据集时，True则覆盖本地已有同名数据集，False则跳过本次下载
    :param save_path: 本地保存路径，若使用默认参数值则保存在$HOME/dexdata/ds/.stereo/v1/路径下面
    :return: 保存到本地的路径字符串列表
    """
    local_path_list = []

    all_projects = load_project_names()
    if len(all_projects) == 0:
        return local_path_list

    for data_project_name in all_projects:
        nas_url = NAS_BASE_URL + data_project_name
        if save_path is None:
            save_path = _VERSIONED_PATH

        local_path = os.path.join(save_path, data_project_name)

        if os.path.exists(local_path):
            if overwrite:
                remove_directory(local_path)
                __download(nas_url, local_path, keep_url_dir=False)
            else:
                pass
        else:
            __download(nas_url, local_path, keep_url_dir=False)

        local_path_list.append(local_path)

    return local_path_list


def get_data_project(
    data_project_name: str, overwrite: bool, save_path: str = None
) -> str:
    """
    根据项目名称从NAS获取对应的数据集并保存到指定的本地路径，同时根据overwrite的值决定覆盖本地已有同名数据集还是跳过下载
    :param data_project_name: NAS上数据集名称（格式：类型/名称，比如'label/scene_000001'）
    :param overwrite: 当本地目录下已经存在同名数据集时，True则覆盖本地已有同名数据集，False则跳过本次下载
    :param save_path: 本地保存路径，若使用默认参数值则保存在$HOME/dexdata/ds/.stereo/v1/路径下面
    :return: 保存到本地的路径字符串
    """
    nas_url = NAS_BASE_URL + data_project_name
    if save_path is None:
        save_path = _VERSIONED_PATH

    local_path = os.path.join(save_path, data_project_name)

    if os.path.exists(local_path):
        if overwrite:
            remove_directory(local_path)
            __download(nas_url, local_path, keep_url_dir=False)
        else:
            pass
    else:
        __download(nas_url, local_path, keep_url_dir=False)

    return local_path


def load_project_names() -> List[str]:
    """
    列举NAS上所有数据集类型和数据集名称组成的列表
    :return: 数据集类型/数据集名称 组成的列表，例如：['label/scene_000001', 'unlabel/scene_000001', 'unlabel/scene_000002', ...]
    """
    result_project_names = []

    label_names = __list_subdir_names(target_url=NAS_BASE_URL)
    if len(label_names) == 0:
        return result_project_names

    nas_base_url_format = (
        NAS_BASE_URL if NAS_BASE_URL.endswith("/") else f"{NAS_BASE_URL}/"
    )
    for label in label_names:
        target_url = nas_base_url_format + label
        cur_project_names = __list_subdir_names(target_url=target_url)
        if len(cur_project_names) > 0:
            label_project_names = ["/".join([label, i]) for i in cur_project_names]
            result_project_names.extend(label_project_names)

    return result_project_names


def __list_subdir_names(target_url: str) -> List[str]:
    """
    列举NAS上给定路径下所有的一级子目录名称列表
    :return: 一级子目录名称列表
    """
    subdir_names = []
    response = __get(target_url)
    if not response:
        return subdir_names
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
            subdir_name = urllib.parse.unquote(pure_link)
            subdir_names.append(subdir_name)

    return subdir_names


# if __name__ == "__main__":
#     proj_names = get_all_data_projects(overwrite=True)
#     print(proj_names)
# save_path = "E:\\data"
# result = get_data_project(proj_names[1], overwrite=False, save_path=save_path)
# print(result)
