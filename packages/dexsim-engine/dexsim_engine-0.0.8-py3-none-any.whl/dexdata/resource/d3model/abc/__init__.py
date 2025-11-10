# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
"""A package for downloading and processing abc dataset."""
import glob
import json
import multiprocessing
import os
import urllib.request
import warnings
from typing import Dict, List, Tuple
from dexdata.resource.d3model import D3MODEL_BASE_PATH

__version__ = "0.0.4"

BASE_PATH = os.path.join(D3MODEL_BASE_PATH, ".abc")
_VERSIONED_PATH = os.path.join(BASE_PATH, "v1")
download_log_file_path = os.path.join(_VERSIONED_PATH, "download.json")

cfg = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "configs",
    "cfg.json",
)

abc_object_file_name = ""
abc_object_file_url = ""
uid_object_url_dict = {}

with open(cfg, "r", encoding="utf-8") as f:
    cfg_data = json.load(f)
    abc_object_file_name = cfg_data.get("abc").get("uid_objects_name")
    abc_object_file_url = (
        "http://"
        + cfg_data.get("minio").get("endpoint")
        + "/"
        + cfg_data.get("abc").get("bucket")
        + "/"
        + abc_object_file_name
    )


def _load_object_paths() -> Dict[str, str]:
    """Load the object paths from the dataset.

    The object paths specify the location of where the object is located
    in the MinIO storage system.

    Returns:
        A dictionary mapping the uid to the object path.
    """
    global abc_object_file_url, abc_object_file_name, uid_object_url_dict
    local_path = os.path.join(_VERSIONED_PATH, abc_object_file_name)
    if not os.path.exists(local_path):
        url = abc_object_file_url
        # wget the file and put it in local_path
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        urllib.request.urlretrieve(url, local_path)
    with open(local_path, "r", encoding="utf-8") as f:
        object_paths = json.load(f)
    uid_object_url_dict = object_paths
    return object_paths


def load_uids() -> List[str]:
    """Load the uids from the dataset.

    Returns:
        A list of uids.
    """
    return list(_load_object_paths().keys())


def _download_object(
    uid: str,
    object_path: str,
    total_downloads: float,
    start_file_count: int,
    object_url: str,
) -> Tuple[str, str]:
    """Download the object for the given uid.

    Args:
        uid: The uid of the object to load.
        object_path: The file path saved to the local disk.
        object_url: The downloading url of the object corresponding to the uid.

    Returns:
        The uid and local path of where the object was downloaded.
    """
    print(f"downloading {uid}")
    local_path = os.path.join(_VERSIONED_PATH, object_path)
    tmp_local_path = os.path.join(_VERSIONED_PATH, object_path + ".tmp")
    # wget the file and put it in local_path
    os.makedirs(os.path.dirname(tmp_local_path), exist_ok=True)
    urllib.request.urlretrieve(object_url, tmp_local_path)

    os.rename(tmp_local_path, local_path)

    files = glob.glob(os.path.join(_VERSIONED_PATH, "abcs", "*", "*.obj"))
    print(
        "Downloaded",
        str(len(files) - start_file_count),
        "/",
        str(total_downloads),
        "objects",
    )

    return uid, local_path


def load_objects(uids: List[str], download_processes: int = 1) -> Dict[str, str]:
    """Return the path to the object files for the given uids.

    If the object is not already downloaded, it will be downloaded.

    Args:
        uids: A list of uids.
        download_processes: The number of processes to use to download the objects.

    Returns:
        A dictionary mapping the object uid to the local path of where the object
        downloaded.
    """
    object_paths = _load_object_paths()
    out = {}
    if download_processes == 1:
        uids_to_download = []
        for uid in uids:
            if uid not in object_paths:
                warnings.warn(f"Could not find object with uid {uid}. Skipping it.")
                continue

            object_url = object_paths[uid]
            obj_file_name = object_url.split("/")[-1]
            subdir_name = obj_file_name.split("_")[0]
            object_path = os.path.join(
                "abcs", subdir_name, obj_file_name
            )  # object_path: abcs/00039989/00039989_277e142b88d749e78a8d4409_trimesh_000.obj

            local_path = os.path.join(_VERSIONED_PATH, object_path)
            if os.path.exists(local_path):
                out[uid] = local_path
                continue
            uids_to_download.append((uid, object_path))
        if len(uids_to_download) == 0:
            return out
        start_file_count = len(
            glob.glob(os.path.join(_VERSIONED_PATH, "abcs", "*", "*.obj"))
        )
        for uid, object_path in uids_to_download:
            uid, local_path = _download_object(
                uid,
                object_path,
                len(uids_to_download),
                start_file_count,
                object_paths[uid],
            )
            out[uid] = local_path
    else:
        args = []
        for uid in uids:
            if uid not in object_paths:
                warnings.warn(f"Could not find object with uid {uid}. Skipping it.")
                continue

            object_url = object_paths[uid]
            obj_file_name = object_url.split("/")[-1]
            subdir_name = obj_file_name.split("_")[0]
            object_path = os.path.join(
                "abcs", subdir_name, obj_file_name
            )  # object_path: abcs/00039989/00039989_277e142b88d749e78a8d4409_trimesh_000.obj

            local_path = os.path.join(_VERSIONED_PATH, object_path)
            if not os.path.exists(local_path):
                args.append((uid, object_path))
            else:
                out[uid] = local_path
        if len(args) == 0:
            return out
        print(
            f"starting download of {len(args)} objects with {download_processes} processes"
        )
        start_file_count = len(
            glob.glob(os.path.join(_VERSIONED_PATH, "abcs", "*", "*.obj"))
        )
        args_list = [
            (*arg, len(args), start_file_count, object_paths[arg[0]]) for arg in args
        ]
        with multiprocessing.Pool(download_processes) as pool:
            r = pool.starmap(_download_object, args_list)
            for uid, local_path in r:
                out[uid] = local_path
    __update_download_log(out)
    return out


def __update_download_log(dict_to_save: Dict[str, str]):
    """
    Update the contents of download.json file.

    Args:
        dict_to_save: dict to update.

    Returns:
        None
    """
    exist_download_log_dict = __read_download_log()
    if exist_download_log_dict is not None:
        exist_download_log_dict.update(dict_to_save)
        __save_download_log(exist_download_log_dict)
    else:
        __save_download_log(dict_to_save)


def __save_download_log(dict_to_save: Dict[str, str]):
    """
    Save the dict to download.json file.
    Args:
        dict_to_save: dict to save.
    Returns:
        None
    """
    with open(download_log_file_path, "w", encoding="utf-8") as f:
        json.dump(dict_to_save, f)


def __read_download_log() -> Dict[str, str]:
    """
    Read contents of the downloa.json file.
    Args:
        None
    Returns:
        Dict
    """
    if not os.path.exists(download_log_file_path):
        # warnings.warn(f"Download log file not exists:{download_log_file_path}")
        return None
    with open(download_log_file_path, "r", encoding="utf-8") as f:
        download_log = json.load(f)
    return download_log


def get_local_objects() -> Dict[str, str]:
    """
    Return the dict mapping uid to the local path.
    Args:
        None
    Returns:
        A dictionary mapping the object uid to the local path of where the object
        downloaded.
    """
    download_log = __read_download_log()
    return download_log
