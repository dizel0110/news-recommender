"""Download N last modified news from S3 storage to files/memory or count news total

Requirements:
    Install boto3:
        pip install boto3

    Configure S3 credentials using one of the suggested methods:
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials

Examples:
    Count news:
        main()
        python news.py
    Last 10 news to python dicts:
        main(kind='memory', n=10)
        python news.py memory 10
    Last 30 news objects to downloads/ dir:
        main(kind='files', n=30, output='downloads')
        python news.py files 30 -o downloads
    All news to news/ dir:
        main(kind='files', n=None)
        python news.py files
"""

import json
from pathlib import Path
import argparse
from pprint import pprint

import boto3


def main(kind='count', n=None, output='news',
         aws_access_key_id=None,
         aws_secret_access_key=None):
    s3 = boto3.resource(service_name='s3',
                        region_name='ru-central1',
                        endpoint_url='https://storage.yandexcloud.net',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)
    bucket = s3.Bucket('yanr')
    os = bucket.objects.filter(Prefix="news/")
    if kind == 'count':
        return sum(1 for _ in os)
    elif kind == 'files':
        n = min(sum(1 for _ in os), n) if n is not None else sum(1 for _ in os)
        output = Path(output)
        output.mkdir(exist_ok=True, parents=True)
        for i, o in enumerate(
                sorted(os, key=lambda x: x.last_modified, reverse=True)[:n]):
            p = output / o.key[5:]
            print(f'{i + 1}/{n} {o.last_modified} {o.key} -> {p}')
            bucket.download_file(o.key, str(p))
    elif kind == 'memory':
        n = min(sum(1 for _ in os), n) if n is not None else sum(1 for _ in os)
        news = []
        for i, o in enumerate(
                sorted(os, key=lambda x: x.last_modified, reverse=True)[:n]):
            d = json.loads(o.get()['Body'].read().decode())
            print(f'{i + 1}/{n} {o.last_modified} {d.get("title", "")}')
            news.append(d)
        return news
    else:
        raise ValueError(kind)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', nargs='?', default='count')
    parser.add_argument('n', nargs='?', type=int, default=None)
    parser.add_argument('-o', '--output', help='directory name', default='news')
    kwargs = vars(parser.parse_args())
    pprint(kwargs)

    r = main(**kwargs)
    pprint(r)
