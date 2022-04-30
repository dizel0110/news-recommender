from yanr.parser.world_nuclear import WorldNuclear


def test_world_nuclear_status200(request, monkeypatch):
    p = WorldNuclear()
    returned_dict = p.get_news_links()
    assert returned_dict['status'] == 200
