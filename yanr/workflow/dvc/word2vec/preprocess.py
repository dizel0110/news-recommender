import string
import json
from pathlib import Path
from collections import Counter
import time
from pprint import pprint
import sys

import pandas as pd
import numpy as np
import yaml
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


class Preprocessor:
    def __init__(
            self,
            kind='yanr',
            raw_path='data/raw/yanr_10k.csv',
            processed_path='data/processed/yanr_10k.txt',
            map_path='data/processed/yanr_10k_map.txt',
            coins_path='data/external/coins.json',
            report_path='reports/data/processed/report.json',
            words_path='reports/data/processed/words.csv',
            words_lengths_path='reports/data/processed/words_lengths.csv',
            sentences_lengths_path='reports/data/processed/sentences_lengths.csv',
            remove_punctuation=True, remove_non_alnum=True, leave_coins_uppercase=True,
            normalize=True, remove_stopwords=True, min_word_length=2,
            min_sentence_length=2, stopwords=(), normalizer='WordNetLemmatizer'):
        self.kind = kind
        self.raw_path = raw_path
        self.processed_path = processed_path
        self.map_path = map_path
        self.coins_path = coins_path
        self.report_path = report_path
        self.words_path = words_path
        self.words_lengths_path = words_lengths_path
        self.sentences_lengths_path = sentences_lengths_path
        self.remove_punctuation = remove_punctuation
        self.remove_non_alnum = remove_non_alnum
        self.leave_coins_uppercase = leave_coins_uppercase
        self.normalize = normalize
        self.remove_stopwords = remove_stopwords
        self.min_word_length = min_word_length
        self.min_sentence_length = min_sentence_length
        self.normalizer = normalizer
        self.stopwords = stopwords

    def __call__(self):
        start_time = time.perf_counter()
        if self.normalizer == 'WordNetLemmatizer':
            lemmatizer = WordNetLemmatizer()
        else:
            raise NotImplementedError(self.normalizer)
        stopwords = set(self.stopwords)
        stopwords.update(nltk_stopwords.words('russian'))
        stopwords.update(nltk_stopwords.words('english'))
        self.stopwords = stopwords
        with open(self.coins_path) as f:
            coins = json.load(f)
        names = {v.get('Symbol', None) for k, v in coins.items()}
        # names.update(v.get('CoinName', None) for k, v in coins.items())
        if not self.leave_coins_uppercase:
            names = {x.lower() for x in names}
        if self.kind == 'yanr':
            df = pd.read_csv(self.raw_path)
            cols = ['title', 'summary']
            docs = [[x[y] for y in cols] for _, x in df.iterrows()]
        elif self.kind == 'list':  # [[text, text], [text], ...]
            docs = self.raw_path
        else:
            raise NotImplementedError(self.kind)
        words, words_lengths, sentences, sentences_lengths, = [], [], [], []
        cnt, err = 0, 0
        for i, d in enumerate(docs):  # document in library
            sentences.append([])
            for j, t in enumerate(d):  # text in document
                sentences[i].append([])
                cnt += 1
                print(f'{cnt} {i + 1}/{len(docs)} {j + 1}/{len(d)} {t}')
                try:
                    t = BeautifulSoup(t, features="lxml").get_text()
                except Exception as e:
                    err += 1
                    sentences[i][j].append([])
                    print(e)
                    continue
                ss = [word_tokenize(x) for x in sent_tokenize(t)]  # sentences in text
                if self.remove_punctuation:
                    ss = [[y for y in x if y not in string.punctuation] for x in ss]
                if self.remove_non_alnum:
                    ss = [[y for y in x if y.isalnum()] for x in ss]
                if not self.leave_coins_uppercase:
                    ss = [[y.lower() for y in x] for x in ss]
                else:
                    ss = [[y.lower() if y not in names else y for y in x] for x
                          in ss]
                if self.normalize:
                    ss = [[lemmatizer.lemmatize(y) for y in x] for x in ss]
                if self.remove_stopwords:
                    ss = [[y for y in x if y not in stopwords or y in names]
                          for x in ss]
                for s in ss:
                    ws = [x for x in s if len(x) >= self.min_word_length]
                    if len(ws) >= self.min_sentence_length:
                        if not ' '.join(ws).isspace():
                            sentences[i][j].append(ws)
                            sentences_lengths.append(len(ws))
                            for w in ws:
                                words_lengths.append(len(w))
                                words.append(w)
        report = {}
        for n, n2, p, a in [('words', 'count', self.words_path, words),
                            ('sentences', 'length',
                             self.sentences_lengths_path, sentences_lengths),
                            ('words', 'length', self.words_lengths_path,
                             words_lengths)]:
            d = report.setdefault(n, {}).setdefault(n2, {})
            c = Counter(a)
            mc = c.most_common()
            d['unique'] = len(c)
            d['number'] = len(a)
            vs = a if n2 == 'length' else list(c.values())
            d['sum'] = int(np.sum(vs))
            d['min'] = int(np.min(vs))
            d['max'] = int(np.max(vs))
            d['mean'] = np.mean(vs)
            d['median'] = np.median(vs)
            d['mode'] = mc[0][0] if n2 == 'length' else Counter(vs).most_common(1)[0][0]
            d['q5'] = np.quantile(vs, 0.05)
            d['q25'] = np.quantile(vs, 0.25)
            d['q75'] = np.quantile(vs, 0.75)
            d['q95'] = np.quantile(vs, 0.95)
            if p is not None:
                p = Path(p)
                p.parent.mkdir(exist_ok=True, parents=True)
                df = pd.DataFrame(mc, columns=["item", "count"])
                df.to_csv(p, index=False)
        report['time'] = time.perf_counter() - start_time
        r = report.setdefault('texts', {})
        r['total'] = cnt
        r['errors'] = err
        r['processed'] = cnt - err
        pprint(report)
        if self.report_path is not None:
            report_path = Path(self.report_path)
            report_path.parent.mkdir(exist_ok=True, parents=True)
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
        if self.processed_path is not None and self.map_path is not None:
            pp = Path(self.processed_path)
            pp.parent.mkdir(exist_ok=True, parents=True)
            pm = Path(self.map_path)
            pm.parent.mkdir(exist_ok=True, parents=True)
            with open(pp, 'w', encoding="utf-8") as fp, open(pm, 'w') as fm:
                for i, d in enumerate(sentences):  # document in library
                    for j, t in enumerate(d):  # text in document
                        for k, s in enumerate(t):  # sentence in text
                            if len(s) != 0:
                                fp.write(' '.join(s) + '\n')
                                fm.write(f'{i} {j} {k}\n')
        else:
            return sentences


if __name__ == '__main__':
    if len(sys.argv) > 1:  # config file
        with open(sys.argv[1]) as f:
            kwargs = yaml.safe_load(f)
    else:  # default
        kwargs = {}
    Preprocessor(**kwargs)()
