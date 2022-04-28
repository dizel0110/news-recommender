import functools
from typing import Dict

from yanr.base.base import Base
from yanr.base.base import click_options as base_options


class Parser(Base):
    def __init__(self,
                 source: str = 'example.com',
                 destination: str = 'parsed_data.json') -> None:
        """Base class for preprocessors

        Args:
            source (str): url
            destination (str): url to database or path to file

        Returns: None
        """
        super().__init__(source=source, destination=destination)

    def load(self) -> Dict:
        raise NotImplementedError()


def click_options(func):
    @base_options
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
