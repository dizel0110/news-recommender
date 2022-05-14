from typing import Dict
import time

import click
import feedparser

from yanr.parser.parser import Parser, click_options


class Rss(Parser):
    def __init__(self, source: str, destination: str) -> None:
        """Parse RSS

        Args:
            source (str): url to database or path to file
            destination (str): url to database or path to file

        Returns: None
        """
        super().__init__(source=source, destination=destination)

    def load(self) -> Dict:
        return feedparser.parse(self.source)

    def process(self, data: Dict) -> Dict:
        d = {}
        d['news'] = [
            {'title': x['title'],
             'text': x['summary'],
             'datetime': time.strftime('%Y-%m-%dT%H:%M:%SZ', x['published_parsed']),
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
def rss_cli(source, destination):
    Rss(source, destination)()


if __name__ == '__main__':
    rss_cli()
