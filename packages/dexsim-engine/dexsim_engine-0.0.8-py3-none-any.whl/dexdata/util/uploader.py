# ----------------------------------------------------------------------------
# Copyright (c) 2021-2023 DexForce Technology Co., Ltd.
#
# All rights reserved.
# ----------------------------------------------------------------------------
# 该工具用于自动解压ABC数据集中的.7z文件，然后自动上传其中的obj文件到MinIO系统中指定的bucket中。
import sys
import minio


minio_conf = {
    "endpoint": "192.168.4.38:9000",
    "access_key": "dexforce",
    "secret_key": "dexforce123",
    "secure": False,
}


def up_data_minio(bucket, object_name, file_path, content_type):
    result = client.fput_object(
        bucket_name=bucket,
        object_name=object_name,
        file_path=file_path,
        content_type=content_type,
    )
    return result


if __name__ == "__main__":
    client = minio.Minio(**minio_conf)
    bucket_name = sys.argv[1]
    object_name = sys.argv[2]
    file_path = sys.argv[3]
    result = up_data_minio(bucket_name, object_name, file_path, "application/binary")
    endpoint = minio_conf.get("endpoint")
    file_url = "http://" + endpoint + "/" + bucket_name + "/" + object_name
    print(file_url)
