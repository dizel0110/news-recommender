from datetime import datetime

import requests
from bs4 import BeautifulSoup
import click

from yanr.parser.parser import Parser, click_options


class WorldNuclearParser(Parser):
    def __init__(self,
                 source: str = "https://world-nuclear.org/",
                 destination: str = "world-nuclear.json") -> None:
        """Parse latest publications on world-nuclear.org

        Args:
            source (str): url
            destination (str): url to database or path to file

        Returns: None
        """
        super().__init__(source=source, destination=destination)

    def __call__(self) -> None:
        """Parse source and save data to storage

        Returns: None
        """
        pass

    


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def habr_cli(source, destination):
    parser = WorldNuclearParser(source, destination)
    parser()


if __name__ == '__main__':
    parser = WorldNuclearParser()
    parser()