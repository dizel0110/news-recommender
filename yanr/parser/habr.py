import json
# from typing import Dict, List, Union, Mapping, Any
from pathlib import Path

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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        response = requests.get(self.url, headers=headers)

        habr_data = list()

        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            aritcles_items = soup.find_all(
                "article", {"class": "tm-articles-list__item"}
            )

            for article_item in aritcles_items:
                item_dict = self.process_article_tag(article_item)

                if item_dict:
                    habr_data.append(item_dict)

        storage_path = Path(self.storage)
        if storage_path.suffix == ".json":
            with open(storage_path, "w") as fw:
                json.dump(habr_data, fw, indent=2, ensure_ascii=False)
        else:
            raise NotImplementedError("Not implemented storage data in database")

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

        # get hubs
        hubs_tag = article_tag.find("div", {"class": "tm-article-snippet__hubs"})
        article_hubs = [
            tag.find("span").text
            for tag in hubs_tag.find_all(
                "span", {"class": "tm-article-snippet__hubs-item"}
            )
        ]
        article_dict["hubs"] = article_hubs

        # get short summary
        snippet_tags = article_tag.find_all("p")
        if snippet_tags:
            article_snippet = " ".join(snippet_tag.text for snippet_tag in snippet_tags)
        else:
            article_snippet = ""

        article_dict["snippet"] = article_snippet

        return article_dict


def main():
    hp = HabrParser()
    hp()


if __name__ == "__main__":
    main()
