from typing import Dict
from datetime import datetime

import click
import feedparser

from yanr.parser.parser import Parser, click_options


class News3d(Parser):
    def __init__(self,
                 source: str = "https://3dnews.ru/news/rss/",
                 destination: str = "news3d.json") -> None:
        """Parse 3DNews RSS

        Args:
            source (str): url
            destination (str): url to database or path to file

        Returns: None
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
        """Parse source and save data to storage

        Returns: None
        """
        d = self.load()
        d = self.process(d)
        self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def news3d_cli(source, destination):
    News3d(source, destination)()


if __name__ == '__main__':
    news3d_cli()
