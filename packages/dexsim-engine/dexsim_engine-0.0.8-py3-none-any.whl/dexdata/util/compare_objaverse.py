# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os
import glob
import sys
from multiprocessing import Process


def get_file_size(file_path):
    file_size = os.path.getsize(file_path)
    return file_size


def compare_glbs_outer(root_path_1: str, root_path_2: str):
    sub_dir_names = []
    for root, dirs, files in os.walk(root_path_1):
        for d in dirs:
            sub_dir_names.append(d)

    p_list = []
    for sub_dir_name in sub_dir_names:
        dir_path_1 = os.path.join(root_path_1, sub_dir_name)
        dir_path_2 = os.path.join(root_path_2, sub_dir_name)
        p = Process(
            target=compare_glbs_inner,
            kwargs={"dir_path_1": dir_path_1, "dir_path_2": dir_path_2},
        )
        p_list.append(p)
        p.start()
    for p1 in p_list:
        p1.join()


def compare_glbs_inner(dir_path_1: str, dir_path_2: str):
    pattern1 = os.path.join(dir_path_1, f"**{os.path.sep}*" + ".glb")
    pattern2 = os.path.join(dir_path_2, f"**{os.path.sep}*" + ".glb")

    glb_dict1 = {}
    glb_dict2 = {}
    for file in glob.glob(pattern1, recursive=True):
        file_name = file.split(os.sep)[-1]
        file_size = get_file_size(file)
        glb_dict1[file_name] = file_size
    for file in glob.glob(pattern2, recursive=True):
        file_name = file.split(os.sep)[-1]
        file_size = get_file_size(file)
        glb_dict2[file_name] = file_size

    if len(glb_dict1.keys()) != len(glb_dict2.keys()):
        raise Exception(
            f"两边glb文件数量不一致:{dir_path_1}->{str(len(glb_dict1.keys()))},{dir_path_2}->{str(len(glb_dict2.keys()))}"
        )
    else:
        print("双方文件数量一致")

    result_dict = {}

    dict1_keys = glb_dict1.keys()
    dict2_keys = glb_dict2.keys()

    dict1_minus_dict2 = set(dict1_keys) - set(dict2_keys)
    dict2_minus_dict1 = set(dict2_keys) - set(dict1_keys)

    if len(dict1_minus_dict2) > 0 or len(dict2_minus_dict1) > 0:
        if len(dict1_minus_dict2) > 0:
            print(f"仅存在于{dir_path_1}下的glb文件为:{dict1_minus_dict2}")
        if len(dict2_minus_dict1) > 0:
            print(f"仅存在于{dir_path_2}下的glb文件为:{dict2_minus_dict1}")
        raise Exception("双方文件名不一致")

    print("双方文件文件名一致")

    result_files = []
    for key in glb_dict1.keys():
        if glb_dict1[key] != glb_dict2[key]:
            result_files.append(key)

    parent_dir = (
        os.path.dirname(dir_path_1)
        if not dir_path_1.endswith(os.sep)
        else os.path.dirname(dir_path_1[:-1])
    )
    sub_dir_name = (
        dir_path_1.split(os.sep)[-1]
        if not dir_path_1.endswith(os.sep)
        else dir_path_1.split(os.sep)[-2]
    )
    log_file_path = os.path.join(parent_dir, sub_dir_name + "-compare-result.txt")

    with open(log_file_path, mode="w", encoding="utf-8") as f:
        f.write("\n".join(result_files) + "\n")


if __name__ == "__main__":
    print("begin...")
    root_path_1 = sys.argv[1]
    root_path_2 = sys.argv[2]
    compare_glbs_outer(root_path_1, root_path_2)
    print("end")
