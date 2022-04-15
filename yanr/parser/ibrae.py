import copy
import urllib.request as urlRequest
import json
from pathlib import Path

from bs4 import BeautifulSoup, SoupStrainer

from yanr.parser.parser import Parser

class Ibrae(Parser):
    def __init__(self, storage: str = 'ibrae.json',
                 url: str = 'http://www.ibrae.ac.ru/news/38') -> None:
        """Patrsing Ibrae news (www.ibrae.ac.ru/news/38)

        Args:
            storage (str): url to database or path to file
            url (str): url from IBRAE 'http://www.ibrae.ac.ru/news/38'

        Returns: None
        """
        super().__init__(storage=storage)
        self.storage = storage
        self.url = url


    def __call__(self) -> None:
        """Parse source and save data to storage

        Returns: None
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        req = urlRequest.Request(self.url, headers=headers)
        # open the url
        url = urlRequest.urlopen(req)
        # get the source code
        source_code = url.read()
        soup = BeautifulSoup(source_code, 'html.parser')

        news_dict = {}
        hrefs = []

        for headlines in soup.find_all('a', href=True):
            hrefs.append(headlines['href'])

        hrefs_orig = copy.deepcopy(hrefs)
        for items in hrefs_orig:
            if "/newstext/" not in items:
                hrefs.remove(items)

        url_list = []
        for link in hrefs:
            url_list.append('http://www.ibrae.ac.ru' + link)

        for url_it in url_list:
            req = urlRequest.Request(url_it, headers=headers)
            url = urlRequest.urlopen(req)
            source_code = url.read()
            soup = BeautifulSoup(source_code, 'html.parser')

            head = soup.find('body').find_all('p')
            current_news = []
            for x in head:
                current_news.append(x.text.strip())

            news_dict.update({url_it: current_news})

        d = news_dict
        #print(d)
        p = Path(self.storage)
        if p.suffix == '.json':
            with open(p, 'w') as f:
                json.dump(d, f, indent=2)
        else:
            raise NotImplementedError('Database')



if __name__ == '__main__':
    p = Ibrae()
    p()
