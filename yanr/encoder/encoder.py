import functools

from yanr.base.base import Base
from yanr.base.base import click_options as base_options


class Encoder(Base):
    def __init__(self,
                 source: str = 'preprocessed_data.json',
                 destination: str = 'encoded_data.json') -> None:
        """Base class for preprocessors

        Args:
            source (str): url to database or path to file
            destination (str): url to database or path to file

        Returns: None
        """
        super().__init__(source=source, destination=destination)


def click_options(func):
    @base_options
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
