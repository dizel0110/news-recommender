import json
import argparse
from pathlib import Path

from bs4 import BeautifulSoup
import requests


def main():
    url = "https://www.cryptocompare.com/api/data/coinlist/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    data = json.loads(soup.prettify())
    data = data['Data']
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs='?', default='coinlist.json')
    args = parser.parse_args()

    d = main()
    print(f'tokens: {len(d)}')

    p = Path(args.output)
    p.parent.mkdir(exist_ok=True, parents=True)
    with open(p, 'w') as f:
        json.dump(d, f, indent=2)
