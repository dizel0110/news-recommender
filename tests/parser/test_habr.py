import json
from yanr.parser.habr import HabrParser


def test_habr_parser_status200(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = HabrParser()
    p()
    with open('habr.json') as f:
        d = json.load(f)
    assert d['status'] == 200


def test_habr_parser_correct_keys_in_json(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = HabrParser()
    p()
    with open('habr.json') as f:
        d = json.load(f)
    assert 'status' in d.keys()
    assert 'news' in d.keys()
