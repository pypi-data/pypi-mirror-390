# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import logging
import os
import re
import urllib.parse

import requests

BASE_URL = "http://192.168.3.120/PickLight/CI-Data"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def get(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            response.raise_for_status()
    except requests.RequestException as e:
        logging.exception(e)
    else:
        return response


def download_file(url, save_path):
    response = get(url)
    if not response:
        logging.error(f"url错误，将跳过下载该文件：{url} ！！！")
        return
    os.makedirs(save_path, exist_ok=True)
    filepath = os.path.join(save_path, os.path.basename(url))
    logging.info(f"正在下载：{url}")
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                break
            f.write(chunk)
    logging.info(f"下载成功，文件已保存至：{filepath}")


def download(url, save_path):
    response = get(url)
    if not response:
        logging.error(f"url错误！！！")
        return
    content_type = response.headers.get("Content-Type") or response.headers.get(
        "content-type"
    )
    if "text/html" in content_type and re.search(
        r"<title>Index of .*?</title>", response.text
    ):
        # 表示这是一个目录
        url = url if url.endswith("/") else f"{url}/"
        save_path = os.path.join(save_path, url.split(os.sep)[-2])
        for match in re.finditer(r"<a href=\"(?P<link>.*?)\">", response.text):
            link = match.groupdict()["link"]
            if link == "../":
                continue
            child_url = urllib.parse.urljoin(url, link)
            if link.endswith("/"):
                if not urllib.parse.urlparse(url).path.startswith(link):
                    # 目录，需要递归搜索
                    download(child_url, save_path)
            else:
                # 文件
                download_file(child_url, save_path)
    else:
        download_file(url, save_path)
