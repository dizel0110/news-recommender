import json
from yanr.parser.habr import HabrParser


def test_parser(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = HabrParser()
    p()
    with open('habr.json') as f:
        d = json.load(f)
    assert d['status'] == 200