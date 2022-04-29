"""
List of pangrams https://clagnut.com/blog/2380/
"""

import json

from yanr.preprocessor import Stemmer


def test_stemmer_porter(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    destination = 'stemmer_porter_data.json'
    s = Stemmer(source='parsed_data.json',
                destination=destination,
                stemmer='PorterStemmer',
                stemmer_kwargs={'mode': 'NLTK_EXTENSIONS'})
    s()
    with open(destination) as f:
        d = json.load(f)
    assert d['news'][-1]['preprocessed_title'].split()[4] == 'jump'
    assert d['news'][-1]['preprocessed_text'].split()[1] == 'zombi'


def test_stemmer_snowball(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    destination = 'stemmer_snowball_data.json'
    s = Stemmer(source='parsed_data.json',
                destination=destination,
                stemmer='SnowballStemmer',
                stemmer_kwargs={'language': 'russian', 'ignore_stopwords': False})
    s()
    with open(destination) as f:
        d = json.load(f)
    assert d['news'][0]['preprocessed_title'].split()[1] == 'скил'
    assert d['news'][0]['preprocessed_text'].split()[3] == 'нанима'


def test_stemmer_lancaster(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    destination = 'stemmer_lancaster_data.json'
    s = Stemmer(source='parsed_data.json',
                destination=destination,
                stemmer='LancasterStemmer',
                stemmer_kwargs={'rule_tuple': None, 'strip_prefix_flag': False})
    s()
    with open(destination) as f:
        d = json.load(f)
    assert d['news'][-1]['preprocessed_title'].split()[4] == 'jump'
    assert d['news'][-1]['preprocessed_text'].split()[1] == 'zomby'
