import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pprint import pprint
from pathlib import Path
import json
import time


if __name__ == '__main__':
    # pip install requirements/dev.txx
    # Download coinlist: python ../../yanr/utils/coinlist.py
    # Set S3 credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) to PATH
    # Download news: python ../../yanr/utils/news.py files 1000
    # 1000 - number of last news, to download all news - remove this argument

    with open('coinlist.json') as f:
        coinlist = json.load(f)
    print(len(coinlist))
    str2coin = {}
    for coin, data in coinlist.items():
        str2coin.setdefault(data['Name'], set()).add(coin)
        str2coin.setdefault(data['Symbol'], set()).add(coin)
        str2coin.setdefault(data['CoinName'], set()).add(coin)
    for k, v in str2coin.items():
        if len(v) != 1:
            print(k, v)
    # assert all(len(x) == 1 for x in str2coin.values())
    max_news = 30
    news_dir = Path("news")
    cnt = 0
    news_paths = news_dir.iterdir()
    news = []
    for _ in range(max_news):
        p = next(news_paths, None)
        if p is not None:
            with open(p) as f:
                n = json.load(f)
                news.append(n)
    print(len(news))
    # path to news
    results = []
    for n in news:
        r = {x: 0 for x in coinlist}
        published = n.get('published_parsed')
        if published is not None:
            r['date'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', tuple(published))
        r['title'] = n.get('title')
        r['link'] = n.get('link')
        for x in [x.get('term') for x in n.get('tags', [])]:
            if x is not None:
                coins = str2coin.get(x, [])
                for c in coins:
                    r[c] += 1
        for k in ['title', 'summary', 'content', 'comments']:
            text = n.get(k)
            if text is not None:
                if k == 'content':
                    text = ' '.join(x.get('value', '') for x in text)
                for token in text.strip().split():
                    coins = str2coin.get(token.strip(), [])
                    for c in coins:
                        r[c] += 1
        # r['total'] = sum(r[c] for c in coinlist)
        results.append(r)

    df = pd.DataFrame(results)
    print(len(df), len(df.columns))
    to_drop = []
    for c in coinlist:
        if df[c].sum() == 0:
            to_drop.append(c)
    alive = list(set(coinlist).difference(to_drop))
    print(alive)
    df = df.drop(columns=to_drop)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date')
    # df = df[(df['date'] > '2022-05-19') & (df['date'] < '2023-02-01')]
    # df = df.sort_values(by='date')
    df.to_csv('news.csv')

    df = pd.read_csv('news.csv')
    df = df.sort_values(by='date')
    alive = list(set(df.columns) - {'date', 'title', 'link'})
    df['hover'] = df.apply(lambda x: f'<a href="{x["link"]}">{x["title"]}</a>', axis=1)
    print(len(df), len(df.columns))
    df2 = df.copy()
    df.loc[:, alive] = df.loc[:, alive].cumsum()

    # Plot
    fig = px.line(df, x="date", y=alive, log_y=True, title='News')
    for c in alive:
        df3 = df2[df2[c] != 0]
        df3.loc[:, [c]] = df3.loc[:, [c]].cumsum()
        fig.add_trace(
            go.Scatter(mode="markers", x=df3["date"], y=df3[c],
                       marker=dict(color="black"),
                       text=df3['hover'], name=f"news_{c}",
                       hovertemplate='<b>%{text}</b>'))
    fig.write_html('news.html')
