# from typing import Dict, List, Union, Mapping, Any

import requests
from bs4 import BeautifulSoup

from yanr.parser.parser import Parser


class HabrParser(Parser):
    def __init__(
        self, storage: str = "habr.json", url: str = "https://habr.com/ru/all/"
    ) -> None:
        """Parse latest publications on habr.com (https://habr.com/)

        Args:
            storage (str): url to database or path to json file storage
            url (str): url of parsing site

        Returns: None
        """
        super().__init__(storage=storage)
        self.url = url

    def __call__(self) -> None:
        """Parse source and save data to storage

        Returns: None
        """
        habr_data = self.parse_habr_summaries()
        self.save(habr_data)

    def parse_habr_summaries(self):
        """Parse source from habr.com

        Returns: None
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        response = requests.get(self.url, headers=headers)

        habr_data = {"status": response.status_code, "news": []}

        if response.ok:

            soup = BeautifulSoup(response.text, "html.parser")
            aritcles_items = soup.find_all(
                "article", {"class": "tm-articles-list__item"}
            )

            for article_item in aritcles_items:
                item_dict = self.process_article_tag(article_item)

                if item_dict:
                    habr_data["news"].append(item_dict)

        return habr_data

    def process_article_tag(self, article_tag):
        """Get main information about article from the main page habr.com

        Args:
            article_tag: bs4 tag with summary-information about article

        Returns:
            dict {"url": url with full text of article,
                  "title": title of article,
                  "hubs": list of habs (tags),
                  "snippet": short summary about article}
        """

        article_dict = {}

        # get url
        article_rel_url = article_tag.find(
            "a", {"class": "tm-article-snippet__title-link"}
        )["href"]
        article_dict["url"] = f"https://habr.com{article_rel_url}"

        # get title
        article_title = (
            article_tag.find("a", {"class": "tm-article-snippet__title-link"})
            .find("span")
            .text
        )
        article_dict["title"] = article_title

        # get tags
        hubs_tag = article_tag.find("div", {"class": "tm-article-snippet__hubs"})
        article_hubs = [
            tag.find("span").text
            for tag in hubs_tag.find_all(
                "span", {"class": "tm-article-snippet__hubs-item"}
            )
        ]
        article_dict["tags"] = article_hubs

        # get short summary
        snippet_tags = article_tag.find_all("p")
        if snippet_tags:
            article_text = " ".join(snippet_tag.text for snippet_tag in snippet_tags)
        else:
            article_text = ""

        article_dict["text"] = article_text

        return article_dict


def main():
    hp = HabrParser(url="https://habr.com/ru/all/page2/")
    hp()


if __name__ == "__main__":
    main()
