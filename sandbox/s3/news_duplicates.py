from pathlib import Path
import json
import plotly.express as px

import pandas as pd

from yanr.utils import news as get_news

if __name__ == '__main__':
    do_update_news = False
    do_update_csv = False
    max_news = 3000
    csv = 'news.csv'
    csv_path = Path(csv)
    if not csv_path.exists() or do_update_csv:
        csv_path.parent.mkdir(exist_ok=True, parents=True)
        output = 'news'
        output_path = Path(output)
        if not output_path.exists() or do_update_news:
            output_path.mkdir(exist_ok=True, parents=True)
            get_news('files', n=max_news, output=output)
        news_paths = output_path.iterdir()
        news = []
        p = next(news_paths, None)
        while p is not None:
            if max_news is not None and len(news) == max_news:
                p = None
            else:
                with open(p) as f:
                    n = json.load(f)
                    n['hash'] = Path(p).stem
                    news.append(n)
            next(news_paths, None)
        df = pd.DataFrame(news)
        df.to_csv(csv_path)
    else:
        df = pd.read_csv(csv_path)
    print(f'news: {len(df)}')
    print(df.columns)
    duplicates = df[df.duplicated(subset=['link'], keep=False)]
    groups = df.groupby(['link'])
    sizes = groups.size()
    print(f'{len(groups)}/{len(df)}')
    print(sizes.mean())
    print(sizes.max())
    print(sizes.min())
    for link, count in sizes.iteritems():
        print(count, link)
        if count > 1:
            print(groups.get_group(link)[['published', 'summary']].sort_values(
                by=['published']))
    fig = px.histogram(
        sizes.sort_values().astype('str'),
        text_auto=True,
        title=f'{len(groups)}/{len(df)} unique/total news<br>'
              f'~{len(df) / len(groups):.2f} duplicates by news<br>'
              f'~{len(groups) / len(df) * 100:.2f}% unique news')
    fig.update_layout(
        xaxis_title="number of duplicates",
        yaxis_title="number of news",
        bargap=0.2, title_x=0.5, showlegend=False)
    fig.write_html('duplicates.html')
