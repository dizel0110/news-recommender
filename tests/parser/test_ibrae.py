import json

from yanr.parser.ibrae import Ibrae


def test_ibrae(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Ibrae()
    p()
    with open('ibrae.json') as f:
        d = json.load(f)
    assert d['status'] == 200
