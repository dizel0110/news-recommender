from urllib.parse import urlparse

import yaml


def parse(feed):
    o = urlparse(feed)
    if o.path.endswith('/'):
        return o.netloc + o.path[:-1]
    else:
        return o.netloc + o.path


if __name__ == '__main__':
    new_file = 'new.txt'
    old_file = '../../yanr/workflow/ray/parse_feeds/config.yaml'
    candidates_file = 'candidates.yaml'
    print(f'Reading new file: {new_file}')
    with open(new_file) as f:
        new_feeds = f.read().strip().split()
    print(f'Reading old file: {old_file}')
    with open(old_file) as f:
        old_feeds = list(yaml.safe_load(f).get('feeds', {}).keys())
    print(f'Number of new feeds: {len(new_feeds)}')
    print(f'Number of old feeds: {len(new_feeds)}')
    unique_new_feeds = set(new_feeds)
    print(f'Number of unique news feeds: {len(unique_new_feeds)}')
    unique_old_feeds = set(old_feeds)
    print(f'Number of unique old feeds: {len(unique_old_feeds)}')
    parsed_news_feeds = {parse(x): x for x in unique_new_feeds}
    print(f'Number of parsed new feeds: {len(parsed_news_feeds)}')
    parsed_old_feeds = {parse(x): x for x in unique_old_feeds}
    print(f'Number of parsed old feeds: {len(parsed_old_feeds)}')
    candidates = {v: True for k, v in parsed_news_feeds.items()
                  if k not in parsed_old_feeds}
    print(f'Number of possible candidates: {len(candidates)}')
    assert len(set(candidates).intersection(old_feeds)) == 0
    print(f'Writing candidates to {candidates_file}')
    with open(candidates_file, 'w') as f:
        yaml.safe_dump(candidates, f)
