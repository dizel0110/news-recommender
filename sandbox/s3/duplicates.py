from pathlib import Path
import json
from urllib.parse import urlparse
import time
from pprint import pprint

import plotly.express as px
import pandas as pd
import boto3
from botocore.errorfactory import ClientError

from yanr.utils import news as download_news


def get_data(do_download_news, max_news, do_update_csv):
    csv_path = Path('news.csv')
    if do_update_csv:
        csv_path.parent.mkdir(exist_ok=True, parents=True)
        output = 'news'
        output_path = Path(output)
        if do_download_news:
            output_path.mkdir(exist_ok=True, parents=True)
            download_news('files', n=max_news, output=output)
        news_paths = output_path.iterdir()
        news = []
        p = next(news_paths, None)
        while p is not None:
            if max_news is not None and len(news) == max_news:
                p = None
                continue
            else:
                with open(p) as f:
                    n = json.load(f)
                    n['key'] = 'news/' + Path(p).name
                    published_parsed = n.get('published_parsed', None)
                    if published_parsed is not None:
                        published_parsed = time.strftime(
                            '%Y-%m-%dT%H:%M:%SZ', tuple(published_parsed))
                    n['published_parsed'] = published_parsed
                    news.append(n)
            print(f'{len(news)}')
            p = next(news_paths, None)
        df = pd.DataFrame(news)
        df['published_parsed'] = pd.to_datetime(df['published_parsed'])
        df.to_csv(csv_path)
    else:
        df = pd.read_csv(csv_path)
    return df


def find_duplicates(df, columns, flts):
    for f in flts:
        df = df[df.apply(f, axis=1)]
    return df.groupby(columns)


def remove_duplicates(groups, aws_access_key_id, aws_secret_access_key):
    to_remove = set()
    if do_remove_duplicates:
        for item, count in groups.size().iteritems():
            g = groups.get_group(item).sort_values(by='published_parsed')
            rows = g.iterrows()
            for _ in range(count - 1):
                i, r = next(rows)
                to_remove.add(r['key'])
            assert next(rows, None) is not None
            assert next(rows, None) is None
    print(f'{len(to_remove)} objects to remove')
    if len(to_remove) != 0:
        not_removed = {}
        cnt = 0
        for key in to_remove:
            cnt += 1
            s3 = boto3.resource(service_name='s3',
                                region_name='ru-central1',
                                endpoint_url='https://storage.yandexcloud.net',
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
            o = s3.Object('yanr', key)
            try:
                o.load()  # Head
            except ClientError as e:  # Key doesn't exist or another error
                not_removed[key] = e
                print(f'{cnt}/{len(to_remove)} {key} BAD: {e}')
            else:
                try:
                    r = o.delete()
                    # 204 is OK https://github.com/boto/boto3/issues/759
                    print(f'{cnt}/{len(to_remove)} {key} OK: {r}')
                except ClientError as e:  # Error while deleting
                    not_removed[key] = e
                    print(f'{cnt}/{len(to_remove)} {key} BAD: {e}')
        print(f'{len(to_remove) - len(not_removed)}/{len(to_remove)} objects removed')
        if len(not_removed) > 0:
            print('Not removed:')
            pprint(not_removed)


def plot_duplicates(groups):
    sizes = groups.size()
    print(f'Instances by one news (min, max, mean, median): '
          f'{sizes.min()} {sizes.max()} {sizes.mean()} {sizes.median()}')
    hostnames = {}
    for item, count in sizes.iteritems():
        if count > 1:
            o = groups.get_group(item)['link']
            o = urlparse(o.values[0])
            h = hostnames.setdefault(o.hostname, {'news': 0, 'instances': 0})
            h['news'] += 1
            h['instances'] += count
    print(f'Hostnames')
    pprint(hostnames)
    fig = px.histogram(
        sizes.sort_values().astype('str'),
        text_auto=True,
        title=f'{len(groups)}/{len(df)} unique/total news<br>'
              f'~{len(df) / len(groups):.2f} instances by one news<br>'
              f'~{len(groups) / len(df) * 100:.2f}% unique news')
    fig.update_layout(
        xaxis_title="number of instances",
        yaxis_title="number of news",
        bargap=0.2, title_x=0.5, showlegend=False)
    fig.write_html('duplicates.html')


if __name__ == '__main__':
    columns = ['link', 'title', 'summary']  # Columns to find duplicates
    flts = []  # Row filters (should return True or False)
    # flts = [lambda x: 'bitrss.com' in x['link']]
    do_download_news = False  # Download news from S3
    max_news = None  # Number of news to download. None - all news
    do_update_csv = False  # Update intermediate CSV file
    do_plot_duplicates = True  # Plot duplicates to html histogram
    do_remove_duplicates = False  # Remove duplicates from S3. Use carefully!
    aws_access_key_id = None  # If None using env variable
    aws_secret_access_key = None  # If None using env variable
    # Print some args
    print(f'columns: {columns}')
    print(f'max_news: {max_news}')
    # Get data
    df = get_data(do_download_news, max_news, do_update_csv)
    # Find duplicates
    groups = find_duplicates(df, columns, flts)
    print(f'{len(groups)}/{len(df)} - unique/total news')
    # Plot duplicates
    if do_plot_duplicates:
        plot_duplicates(groups)
    # Remove duplicates
    if do_remove_duplicates:
        remove_duplicates(groups, aws_access_key_id, aws_secret_access_key)
