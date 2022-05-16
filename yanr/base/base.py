import json
from pathlib import Path
import functools
from urllib.parse import urlparse

import click


class Base:
    def __init__(self, source, destination):
        """Abstract class for all classes

        Args:
            source (str or dict or None): url/path, dict or None
            destination (str or dict or None): url/path, dict or None

        Returns: dict or None
        """
        self.source = source
        self.destination = destination

    def __call__(self):
        """Load data from source, process and return/save to destination
        """
        d = self.load()
        # Process data ...
        return self.save(d)

    def load(self):
        """Load data from source

        Returns: dict or None
        """
        if isinstance(self.source, dict) or self.source is None:
            data = self.source
        elif isinstance(self.source, str):
            r = urlparse(self.source)
            if r.scheme in ['', 'file']:
                p = Path(r.path)
                with open(p) as f:
                    if p.suffix == '.json':
                        data = json.load(f)
                    else:
                        raise ValueError('Only json is allowed')
            else:
                raise NotImplementedError('Database connection')
        else:
            raise ValueError('Source can by str or dict only')
        return data

    def save(self, data):
        """Return/save data to destination

        Args:
            data (dict or None): data to save or return

        Returns: dict or None
        """
        if self.destination is None:
            return data
        elif isinstance(self.destination, str):
            r = urlparse(self.destination)
            if r.scheme in ['', 'file']:
                p = Path(self.destination).resolve()
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "w") as f:
                    if p.suffix == ".json":
                        json.dump(data, f, indent=2)
                    else:
                        raise ValueError('Only json is allowed')
            else:
                raise NotImplementedError('Database connection')
        else:
            raise ValueError('Destination can be str or None only')


def click_options(func):
    @click.option('-s', '--source', default=None, help='url/path')
    @click.option('-d', '--destination', default=None, help='url/path')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
