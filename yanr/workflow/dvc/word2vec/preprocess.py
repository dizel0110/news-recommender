import string
import json
from pathlib import Path

import pandas as pd
import click
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


@click.command()
@click.option('--kind', '-k', help='Kind of dataset')
@click.option('--input-path', '-i', help='Path to dataset')
@click.option('--output-path', '-o', help='Path to output file')
@click.option('--coins-path', help='Path to file with coins description')
@click.option('--leave-coins-uppercase', default=1, help='Leave coins names uppercase?')
@click.option('--remove-punctuation', default=1, help='Remove punctuation?')
@click.option('--remove-non-alnum', default=1,
              help='Remove non alphabetic/numerical chars?')
@click.option('--remove-stopwords', default=1, help='Remove stopwords?')
@click.option('--lemmatize', default=1, help='Lemmatize words?')
@click.option('--min-sentence-length', default=2, help='Minimum sentence length')
@click.option('--min-word-length', default=2, help='Minimum word length')
def main(kind, input_path, output_path, coins_path, leave_coins_uppercase,
         remove_punctuation, remove_non_alnum, lemmatize, remove_stopwords,
         min_sentence_length, min_word_length):
    if kind == 'yanr':
        df = pd.read_csv(input_path)
        cols = ['title', 'summary']
    else:
        raise NotImplementedError(kind)
    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    lmt = WordNetLemmatizer()
    sws = set(stopwords.words('english'))
    sws.update(stopwords.words('russian'))
    if leave_coins_uppercase is not None:
        with open(coins_path) as f:
            coins = json.load(f)
        names = {v.get('Symbol', None) for k, v in coins.items()}
        names.update(v.get('CoinName', None) for k, v in coins.items())
    else:
        names = set()
    with open(output_path, 'w', encoding="utf-8") as f:
        for index, row in df.iterrows():
            for c in cols:
                t = row[c]
                print(f'{index + 1}/{len(df)} {c} {t}')
                try:
                    t = BeautifulSoup(t, features="lxml").get_text()
                except Exception as e:
                    print(e)
                    continue
                ss = [word_tokenize(x) for x in sent_tokenize(t)]
                if remove_punctuation:
                    ss = [[y for y in x if y not in string.punctuation] for x in ss]
                if remove_non_alnum:
                    ss = [[y for y in x if y.isalnum()] for x in ss]
                if not leave_coins_uppercase:
                    ss = [[y.lower() for y in x] for x in ss]
                else:
                    ss = [[y.lower() if y not in names else y for y in x] for x in ss]
                if lemmatize:
                    ss = [[lmt.lemmatize(y) for y in x] for x in ss]
                if remove_stopwords:
                    ss = [[y for y in x if y not in sws or y in names] for x in ss]
                for s in ss:
                    if len(s) >= min_sentence_length:
                        s = ' '.join(x for x in s if len(x) >= min_word_length)
                        if len(s) > 0:
                            print(s)
                            f.write(s + '\n')


if __name__ == '__main__':
    main()
