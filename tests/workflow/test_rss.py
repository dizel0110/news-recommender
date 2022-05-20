from yanr.getter.url import Url
from yanr.parser.rss import Rss
from yanr.preprocessor.cleaner import Cleaner
from yanr.preprocessor.morpher import Morpher


def test_rss(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    u = Url(source='https://3dnews.ru/news/rss/', destination='3dnews.html')
    r = Rss(source='3dnews.html', destination=None)
    u_out = u()
    assert u_out is None
    r_out = r()
    assert isinstance(r_out, dict)
    c = Cleaner(source=r_out, destination=None)
    c_out = c()
    assert isinstance(c_out, dict)
    m = Morpher(source=c_out, destination=None)
    m_out = m()
    assert isinstance(m_out, dict)
