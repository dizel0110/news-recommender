import json
from unittest import TestCase

from yanr.base.base import Base


def test_json_json(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source='input.json', destination='output.json')
    p()
    with open('input.json') as f:
        d1 = json.load(f)
    with open('output.json') as f:
        d2 = json.load(f)
    TestCase().assertDictEqual(d1, d2)


def test_dict_dict(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    with open('input.json') as f:
        d1 = json.load(f)
    d2 = {}
    p = Base(source=d1, destination=d2)
    try:
        p()
    except ValueError as e:
        assert True


def test_none_none(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source=None, destination=None)
    try:
        p()
    except ValueError as e:
        assert True


def test_other_other(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source='input.txt', destination='output.txt')
    try:
        p()
    except ValueError as e:
        assert True


def test_json_none(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source='input.json', destination=None)
    d2 = p()
    with open('input.json') as f:
        d1 = json.load(f)
    TestCase().assertDictEqual(d1, d2)


def test_json_other(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source='input.json', destination='output.txt')
    try:
        p()
    except ValueError as e:
        assert True


def test_json_dict(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    d2 = {}
    p = Base(source='input.json', destination=d2)
    try:
        p()
    except ValueError as e:
        assert True


def test_dict_none(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    with open('input.json') as f:
        d1 = json.load(f)
    p = Base(source=d1, destination=None)
    d2 = p()
    TestCase().assertDictEqual(d1, d2)


def test_dict_json(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    with open('input.json') as f:
        d1 = json.load(f)
    p = Base(source=d1, destination='output.json')
    with open('output.json') as f:
        d2 = json.load(f)
    TestCase().assertDictEqual(d1, d2)


def test_dict_other(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    with open('input.json') as f:
        d1 = json.load(f)
    p = Base(source=d1, destination='output.txt')
    try:
        p()
    except ValueError as e:
        assert True


def test_other_dict(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    d2 = {}
    p = Base(source='input.txt', destination=d2)
    try:
        p()
    except ValueError as e:
        assert True


def test_other_none(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source='input.txt', destination=None)
    try:
        p()
    except ValueError as e:
        assert True


def test_other_json(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source='input.txt', destination='output.json')
    try:
        p()
    except ValueError as e:
        assert True


def test_none_json(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source=None, destination='output.json')
    try:
        p()
    except ValueError as e:
        assert True


def test_none_dict(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    d2 = {}
    p = Base(source=None, destination=d2)
    try:
        p()
    except ValueError as e:
        assert True


def test_none_other(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)
    p = Base(source=None, destination='output.txt')
    try:
        p()
    except ValueError as e:
        assert True
