import json

from yanr.parser.news3d import News3d


def test_news3d(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = News3d()
    p()
    with open('news3d.json') as f:
        d = json.load(f)
    assert d['status'] == 200
