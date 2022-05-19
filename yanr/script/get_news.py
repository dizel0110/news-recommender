"""Download N last mofdifed objects from S3 storage to files or to memory examples

Requirements:
    pip install boto3

Examples:
    Last 10 last objects to python dicts
    in_memory(10)
    All files to files in objects/ dir
    in_files(None)
    30 last objects to files in downloads/ dir
    in_files(30, 'downloads')
"""

import boto3
import json
from pathlib import Path


def to_files(n=10, dir_path='objects'):
    s3 = boto3.resource(service_name='s3',
                        region_name='ru-central1',
                        endpoint_url='https://storage.yandexcloud.net',
                        aws_access_key_id='',
                        aws_secret_access_key='')
    bucket = s3.Bucket('yanr')
    objects = bucket.objects.filter(Prefix="news/")
    n = min(sum(1 for _ in objects), n) if n is not None else sum(1 for _ in objects)
    dir_path = Path(dir_path)
    dir_path.mkdir(exist_ok=True, parents=True)
    for i, o in enumerate(
            sorted(objects, key=lambda x: x.last_modified, reverse=True)[:n]):
        file_name = o.key[5:]  # remove prefix
        file_path = dir_path / file_name
        print(f'{i + 1}/{n} {o.last_modified} {o.key} -> {file_path}')
        bucket.download_file(o.key, str(file_path))


def to_memory(n=10):
    s3 = boto3.resource(service_name='s3',
                        region_name='ru-central1',
                        endpoint_url='https://storage.yandexcloud.net',
                        aws_access_key_id='',
                        aws_secret_access_key='')
    bucket = s3.Bucket('yanr')
    objects = bucket.objects.filter(Prefix="news/")
    n = min(sum(1 for _ in objects), n) if n is not None else sum(1 for _ in objects)
    dicts = []
    for i, o in enumerate(
            sorted(objects, key=lambda x: x.last_modified, reverse=True)[:n]):
        d = json.loads(o.get()['Body'].read().decode())
        print(f'{i + 1}/{n} {o.last_modified} {d["title"]}')
        dicts.append(d)
    return dicts


def count():
    s3 = boto3.resource(service_name='s3',
                        region_name='ru-central1',
                        endpoint_url='https://storage.yandexcloud.net',
                        aws_access_key_id='',
                        aws_secret_access_key='')
    bucket = s3.Bucket('yanr')
    objects = bucket.objects.filter(Prefix="news/")
    print(sum(1 for _ in objects))


# to_files(20)
# to_memory(None)
count()
