from typing import Dict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import click

from yanr.parser.parser import Parser, click_options


class WorldNuclear(Parser):
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
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
        }

    def __call__(self) -> None:
        """Parse source and save data to storage

        Returns: None
        """
        world_nuclear_data = self.get_data()
        self.save(world_nuclear_data)

    def get_data(self) -> Dict:
        """Parse all data from the site

        Returns: None
        """
        world_nuclear_data = self.get_news_links()

        for news_dict in world_nuclear_data['news']:
            href = news_dict['href']
            resp = requests.get(href, headers=self.headers)
            if resp.ok:
                soup = BeautifulSoup(resp.text, 'html.parser')
                body_tag = soup.find('div', {'class': 'ArticleBody'})
                # if we didn't find information about published date before
                if 'datetime' not in news_dict.keys():
                    date = datetime.strptime(body_tag.find('p').text, "%d %B %Y")
                    news_dict['datetime'] = date.isoformat()
                text = ' '.join([tag.text for tag in body_tag.find_all('p')][1:-1])
                news_dict['text'] = text
        return world_nuclear_data

    def get_news_links(self) -> Dict:
        """Parse data from the main site. Get hrefs to the page for every news

        Returns: None
        """
        response = requests.get(self.source, headers=self.headers)

        news_list = list()

        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            news_tag = soup.find("div", {"class": "homepageSocialMediaSpacing"})

            for tag in news_tag.find_all("h2"):
                news_dict = {'href': tag.find('a')['href'],
                             'title': tag.text.strip()}

                # date information
                date_str = tag.find_next_sibling("p").text.strip()
                if 'Published: ' in date_str:
                    date_str = date_str.split('Published: ')[1]
                    date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                    news_dict['datetime'] = date.isoformat()

                news_list.append(news_dict)

        return {"status": response.status_code, "news": news_list}


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@click_options
def world_nuclear_cli(source, destination):
    parser = WorldNuclear(source, destination)
    parser()


if __name__ == '__main__':
    world_nuclear_cli()
