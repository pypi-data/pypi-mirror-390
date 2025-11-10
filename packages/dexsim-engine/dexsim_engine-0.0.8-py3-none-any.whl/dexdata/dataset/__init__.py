# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os
from dexdata import DEXDATA_BASE_PATH
from typing import List


DATASET_BASE_PATH = os.path.join(DEXDATA_BASE_PATH, "ds")
standard_ds_names = None


def load_all_project_names() -> List[dict]:
    """
    返回除影子模式数据外其他所有数据集的名称和类型列表
    """
    global standard_ds_names
    from dexdata.dataset import standard

    project_names = standard.load_project_names()
    standard_ds_names = project_names
    return project_names


def get_data_project(data_project_name: str, target_dir: str = None) -> str:
    """
    根据项目名称获取对应的数据集并保存到指定的本地路径
    :param data_project_name: 数据集名称
    :param target_dir: 本地保存路径，若使用默认参数值则保存在$HOME/dexdata/ds/路径下面
    :return: 保存到本地的路径
    """
    global standard_ds_names
    save_path = ""
    for item in standard_ds_names:
        if data_project_name in item.keys():
            from dexdata.dataset import standard

            save_path = standard.get_data_project(
                data_project_name=data_project_name, target_dir=target_dir
            )
            break
    return save_path
