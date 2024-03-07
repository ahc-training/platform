from icecream import ic
from minio import Minio
from minio.error import S3Error
import pendulum
import os
import json


bucket = "raw"

def main():
    client = Minio(
        "data.example.com",
        access_key="sysadmin",
        secret_key="Amh528219898",
        secure=False,
    )
    ic(client.list_buckets())

    found = ic(client.bucket_exists(bucket))
    if found:
        for itm in client.list_objects(bucket):
            obj = ic(itm.object_name)
            b = client.get_object(bucket, obj)
            j = ic(b.json())
            

if __name__ == "__main__":
    last_modified_date = pendulum.from_timestamp(os.path.getmtime(__file__))
    ic(last_modified_date)
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
