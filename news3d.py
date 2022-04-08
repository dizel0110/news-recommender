from pathlib import Path
import json

import feedparser


class News3d:
    def __init__(self, storage='news3d.json', rss='https://3dnews.ru/news/rss/'):
        """Parse 3DNews RSS (https://3dnews.ru/)

        Args:
            storage (str): url to database or path to file
            rss (str): url from 3DNews RSS list https://3dnews.ru/subscribe
        """
        self.storage = storage
        self.rss = rss

    def __call__(self):
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
