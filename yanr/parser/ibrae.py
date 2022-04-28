import copy
import urllib.request as url_request

import click
from bs4 import BeautifulSoup

from yanr.parser.parser import Parser, click_options


class Ibrae(Parser):
    def __init__(self,
                 source: str = "http://www.ibrae.ac.ru/news/38",
                 destination: str = "ibrae.json") -> None:
        """Parse 3DNews RSS

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

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        req = url_request.Request(self.source, headers=headers)
        # open the url
        url = url_request.urlopen(req)
        # get the source code
        source_code = url.read()
        soup = BeautifulSoup(source_code, "html.parser")

        news_dict = {}
        hrefs = []

        for headlines in soup.find_all("a", href=True):
            hrefs.append(headlines["href"])

        hrefs_orig = copy.deepcopy(hrefs)
        for items in hrefs_orig:
            if "/newstext/" not in items:
                hrefs.remove(items)

        url_list = []
        for link in hrefs:
            url_list.append("http://www.ibrae.ac.ru" + link)

        for url_it in url_list:
            req = url_request.Request(url_it, headers=headers)
            url = url_request.urlopen(req)
            source_code = url.read()
            soup = BeautifulSoup(source_code, "html.parser")

            head = soup.find("body").find_all("p")
            current_news = []
            for x in head:
                current_news.append(x.text.strip())

            news_dict.update({url_it: current_news})

        d = news_dict
        # print(d)
        self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def ibrae_cli(source, destination):
    Ibrae(source, destination)()


if __name__ == '__main__':
    ibrae_cli()
