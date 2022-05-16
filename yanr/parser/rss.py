from typing import Dict
import time

import click
import feedparser

from yanr.parser.parser import Parser, click_options


class Rss(Parser):
    def __init__(self, source, destination):
        """Parse RSS

        Args:
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None

        Returns: dict or None
        """
        super().__init__(source=source, destination=destination)

    def load(self):
        return feedparser.parse(self.source)

    def process(self, data: Dict) -> Dict:
        d = {}
        d['news'] = [
            {'title': x.get('title', None),
             'text': x.get('summary', None),
             'datetime': time.strftime('%Y-%m-%dT%H:%M:%SZ', x['published_parsed'])
             if 'published_parsed' in x else None,
             'tags': [y['term'] for y in x['tags']],
             'url': x.get('link', None),
             'author': x.get('author', None)}
            for x in data['entries']]
        return d

    def __call__(self):
        d = self.load()
        d = self.process(d)
        return self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def rss_cli(source, destination):
    Rss(source, destination)()


if __name__ == '__main__':
    rss_cli()
