import json
from pathlib import Path
from typing import Dict
import functools

import click


class Base:
    def __init__(self, source: str, destination: str) -> None:
        """Abstract class for all classes

        Args:
            source (str): url or path to file
            destination (str): url or path to file

        Returns: None
        """
        self.source = source
        self.destination = destination

    def __call__(self) -> None:
        """Load data from source, process and save to destination

        Returns: None
        """
        d = self.load()
        # Process data ...
        self.save(d)

    def load(self) -> Dict:
        p = Path(self.source)
        if p.suffix == '.json':
            with open(p) as f:
                data = json.load(f)
        else:
            raise NotImplementedError('Database')
        return data

    def save(self, data: Dict) -> None:
        """Save data to destination

        Args:
            data (list): list of news

        Returns: None
        """
        p = Path(self.destination).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix == ".json":
            with open(p, "w") as f:
                json.dump(data, f, indent=2)
        else:
            raise NotImplementedError('Database')


def click_options(func):
    @click.option('-s', '--source', help='url or path to file')
    @click.option('-d', '--destination', help='url or path to file')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
