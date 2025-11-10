# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
import os.path
import sys
import uuid
from minio.api import Minio, Tags


minio_conf = {
    "endpoint": "192.168.3.43:9009",
    "access_key": "dexdata",
    "secret_key": "dexdata123.",
    "secure": False,
    "bucket_name": "dex-ds-os-abc",
}


class MinIOHelper:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool,
        bucket_name: str,
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.bucket_name = bucket_name
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def __get_uid_from_str(self, string: str) -> str:
        """Generates a UUID from a string.
        Args:
            string (str): String to generate a UUID from.
        Returns:
            str: UUID generated from the string.
        """
        namespace = uuid.NAMESPACE_DNS
        uid = uuid.uuid5(namespace, string)
        uid_pure = str(uid).replace("-", "")
        return uid_pure

    def upload_data_with_self_name(self, file_path: str, content_type: str):
        """
        Upload local file to MinIO without adding tag, using the processed name as the minio object_name
        Args:
            file_path: file abs path.
            content_type: content type of the file.

        Returns:
            A tuple mapping the file_path to the downloading url in MinIO.
        """
        file_name = file_path.split(os.path.sep)[-1]
        sub_dir_name = file_path.split(os.path.sep)[-2]
        object_name = "_".join([sub_dir_name, file_name])
        bucket_exists = self.client.bucket_exists(self.bucket_name)
        if not bucket_exists:
            raise Exception(f"MinIO bucket {self.bucket_name} does not exist.")
        minio_url = (
            "http://" + self.endpoint + "/" + self.bucket_name + "/" + object_name
        )
        obj_result = self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type,
        )
        return file_path, minio_url

    def upload_data_without_tag(self, file_path: str, content_type: str):
        """
        Upload local file to MinIO without adding tag, using the filename as the minio object_name
        Args:
            file_path: file abs path.
            content_type: content type of the file.

        Returns:
            A tuple mapping the file_path to the downloading url in MinIO.
        """
        file_name = file_path.split(os.path.sep)[-1]
        object_name = file_name
        bucket_exists = self.client.bucket_exists(self.bucket_name)
        if not bucket_exists:
            raise Exception(f"MinIO bucket {self.bucket_name} does not exist.")
        minio_url = (
            "http://" + self.endpoint + "/" + self.bucket_name + "/" + object_name
        )
        obj_result = self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type,
        )
        return file_path, minio_url

    def upload_data_with_auto_generated_uid(self, file_path: str, content_type: str):
        """Upload local file to MinIO
        Args:
            file_path: file abs path.
            content_type: content type of the file.

        Returns:
            A tuple mapping the object uid to the url of MinIO.
        """
        file_name = file_path.split(os.path.sep)[-1]
        object_name = file_name
        uid = self.__get_uid_from_str(file_name)
        bucket_exists = self.client.bucket_exists(self.bucket_name)
        if not bucket_exists:
            raise Exception(f"MinIO bucket {self.bucket_name} does not exist.")
        minio_url = (
            "http://" + self.endpoint + "/" + self.bucket_name + "/" + object_name
        )
        obj_result = self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type,
        )
        tags = Tags.new_object_tags()
        tags["uid"] = uid
        tags["name"] = file_name
        tags["uri"] = minio_url
        self.client.set_object_tags(
            bucket_name=obj_result.bucket_name,
            object_name=obj_result.object_name,
            tags=tags,
            version_id=obj_result.version_id,
        )
        return uid, minio_url


if __name__ == "__main__":
    minio_helper = MinIOHelper(**minio_conf)
    file_path = (
        "D:\\ABC\\bk\\00209981\\00209981_99d0f64c26d188094251ff1c_trimesh_000.obj"
    )
    uid, url = minio_helper.upload_data_with_auto_generated_uid(
        file_path, "application/binary"
    )
    print(uid)
    print(url)
