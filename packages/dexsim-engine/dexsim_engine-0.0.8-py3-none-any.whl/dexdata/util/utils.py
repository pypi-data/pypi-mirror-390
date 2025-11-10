# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import hashlib
import os
import shutil


def get_file_hash(file_path: str) -> str:
    """Get the sha256 hash of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: sha256 hash of the file.
    """
    # Check if the path is a symbolic link
    if os.path.islink(file_path):
        # Resolve the symbolic link
        resolved_path = os.readlink(file_path)
        # Check if the resolved path exists
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(
                f"The symbolic link points to a file that doesn't exist: {resolved_path}"
            )
    sha256 = hashlib.sha256()
    # Read the file from the path
    with open(file_path, "rb") as f:
        # Loop till the end of the file
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()


def remove_directory(dir_path: str) -> bool:
    """
    delete given directory and all its contents.
    """
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        return True
    except OSError as e:
        return False
