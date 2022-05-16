from typing import Dict
from datetime import datetime

import click
import feedparser

from yanr.parser.parser import Parser, click_options


class News3d(Parser):
    def __init__(self, source="https://3dnews.ru/news/rss/", destination="news3d.json"):
        """Parse 3DNews RSS

        Args:
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None

        Returns: dict or None
        """
        super().__init__(source=source, destination=destination)

    def load(self) -> Dict:
        return feedparser.parse(self.source)

    def process(self, data: Dict) -> Dict:
        d = {}
        d['status'] = data['status']
        d['news'] = [
            {'title': x['title'],
             'text': x['summary'],
             'datetime': datetime.strptime(x['published'],
                                           '%a, %d %b %Y %H:%M:%S %z').isoformat(),
             'tags': [y['term'] for y in x['tags']],
             'url': x['link']}
            for x in data['entries']]
        return d

    def __call__(self) -> None:
        d = self.load()
        d = self.process(d)
        return self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def news3d_cli(source, destination):
    News3d(source, destination)()


if __name__ == '__main__':
    news3d_cli()
