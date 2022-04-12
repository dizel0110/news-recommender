from pathlib import Path
import json

import feedparser

from yanr.parser.parser import Parser


class News3d(Parser):
    def __init__(self, storage: str = 'news3d.json',
                 rss: str = 'https://3dnews.ru/news/rss/') -> None:
        """Parse 3DNews RSS (https://3dnews.ru/)

        Args:
            storage (str): url to database or path to file
            rss (str): url from 3DNews RSS list https://3dnews.ru/subscribe

        Returns: None
        """
        super().__init__(storage=storage)
        self.storage = storage
        self.rss = rss

    def __call__(self) -> None:
        """Parse source and save data to storage

        Returns: None
        """
        d = feedparser.parse(self.rss)
        p = Path(self.storage)
        if p.suffix == '.json':
            with open(p, 'w') as f:
                json.dump(d, f, indent=2)
        else:
            raise NotImplementedError('Database')


if __name__ == '__main__':
    p = News3d()
    p()
