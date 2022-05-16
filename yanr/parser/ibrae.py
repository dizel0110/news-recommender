import copy
import urllib

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
        news_dict = {}
        req = urllib.request.Request(self.source, headers=headers)
        # open the url
        url = urllib.request.urlopen(req)
        news_dict['status'] = url.getcode()
        # get the source code
        source_code = url.read()
        soup = BeautifulSoup(source_code, "html.parser")

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
            req = urllib.request.Request(url_it, headers=headers)
            url = urllib.request.urlopen(req)
            source_code = url.read()
            soup = BeautifulSoup(source_code, "html.parser")

            head = soup.find("body").find_all("p")
            current_news = []
            for x in head:
                current_news.append(x.text.strip())

            news_dict.update({url_it: current_news})

        d = {}
        # print(d)
        list_keys = list(news_dict.keys())
        list_values = list(news_dict.values())
        d['status'] = news_dict['status']
        for x in range(len(list_keys)):
            d['news'] = [
                {'title': None,
                 'text': list_values[x],
                 'datetime': None,
                 'tags': None,
                 'url': list_keys[x]}]

        self.save(d)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def ibrae_cli(source, destination):
    Ibrae(source, destination)()


if __name__ == '__main__':
    ibrae_cli()
