import ray
import yaml
import argparse
import json
import hashlib
# from itertools import chain
import time
from pprint import pprint
from datetime import datetime, timedelta
from collections import Counter

import numpy as np
import feedparser
import boto3
from botocore.errorfactory import ClientError

# Parse cmd arguments
parser = argparse.ArgumentParser(description='Parse feeds with Ray')
parser.add_argument('config')
args = parser.parse_args()

# Read configs
with open(args.config) as f:
    cfg = yaml.safe_load(f)

# Initialize Ray
ray.init()


# Define worker
@ray.remote(**cfg['remote_kwargs'])
class Parser:
    def __init__(self, urls, max_cache_size, bucket, prefix,
                 service_name, storage_class, region, endpoint_url):
        self.urls = urls
        self.max_cache_size = max_cache_size
        self.bucket = bucket
        self.prefix = prefix
        self.storage_class = storage_class
        self.cache = set()
        self.session = boto3.session.Session()
        self.client = self.session.client(service_name=service_name,
                                          region_name=region,
                                          endpoint_url=endpoint_url)

    def work(self):
        if len(self.cache) > self.max_cache_size:
            self.cache = set()
        ss = {}  # statuses
        errors = []
        exceptions = {}
        added = 0
        exists = 0
        for u in self.urls:
            try:
                r = feedparser.parse(u)
            except Exception as e:
                exceptions[u] = e
            else:
                ss[u] = r.get('status', None)
                if ss[u] is None or ss[u] != 200:
                    continue
                for entity in r.get('entries', []):
                    h = self.make_hash(entity)
                    if h not in self.cache:
                        k = f'{self.prefix}/{h}.json'
                        result = self.upload(entity, k)
                        if result == 0:
                            errors.append(k)
                        elif result == 1:
                            added += 1
                            self.cache.add(h)
                        elif result == 2:
                            exists += 1
                            self.cache.add(h)
                    else:
                        exists += 1
        return {'statuses': ss, 'errors': errors,
                'exceptions': exceptions,
                'added': added, 'exists': exists,
                'total': added + exists + len(errors),
                'cache_size': len(self.cache)}

    def make_hash(self, entry):
        s = entry.get('link', '') + entry.get('published', '')
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    def upload(self, entry, key):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except ClientError:  # Key doesn't exist or another error
            try:
                self.client.put_object(
                    Bucket=self.bucket, Key=key,
                    Body=json.dumps(entry),
                    StorageClass=self.storage_class)
            except ClientError as e:  # Error
                print(e)
                return 0
            else:  # Key added
                return 1
        else:  # Key already exists
            return 2


num_workers = cfg.get('num_workers', 1)
print(f'num_workers: {num_workers}')
feeds = [k for k, v in cfg['feeds'].items() if v]
print(f'feeds: {len(feeds)}')
pprint(feeds)

# Shuffle and split feeds into chunks
rng = np.random.default_rng(seed=cfg['seed'])
rng.shuffle(feeds)
chunks = np.array_split(feeds, num_workers)
pprint([len(x) for x in chunks])

# Initialize workers
worker = globals()[cfg['worker']]
worker_kwargs = cfg.get('worker_kwargs', {})
worker_kwargss = [{**worker_kwargs, **{'urls': x}} for x in chunks]
workers = [worker.remote(**x) for x in worker_kwargss]
pprint(workers)

# Run workers
interval, timeout = cfg['interval'], cfg['timeout']
print(f'interval: {interval} seconds')
print(f'timeout: {timeout} seconds')
print(f'time start: {datetime.utcnow()}')
print(f'time end ~ {datetime.utcnow() + timedelta(seconds=timeout)}')
print(f'runs ~ {int(timeout / interval)}')

t0 = time.time()
cnt = 0
while time.time() - t0 < timeout:
    t00 = time.time()
    cnt += 1
    print(f'{cnt}. {(t00 - t0) / timeout * 100:.0f}% {datetime.utcnow()}')
    results = ray.get([x.work.remote() for x in workers])
    pprint(results)
    statuses = Counter()  # type: Counter
    for x in results:
        statuses.update(x['statuses'].values())
    print(statuses)
    spent = time.time() - t00
    sleep = interval - spent if interval - spent > 0 else 0
    print(f'time spent: {spent}')
    print(f'time sleep: {sleep}')
    if time.time() - t0 > timeout:
        break
    time.sleep(sleep)
print(f'time end: {datetime.utcnow()}')
print(f'time spent total: {time.time() - t0}')
