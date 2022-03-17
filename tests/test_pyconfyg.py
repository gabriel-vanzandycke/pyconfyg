from pyconfyg import PyConfyg, Confyg, parse_strings

import io

def test_parse_strings():
    assert parse_strings("a=2") == {'a': 2}

def test_parse_strings2():
    assert parse_strings("a=2", "b=4") == {'a': 2, 'b': 4}

def test_parse_strings3():
    env = {'c': 3}
    assert parse_strings("a=2", "b=4", env=env) == {'a': 2, 'b': 4, 'c': 3}

def test_parse_strings4():
    assert parse_strings("a=2\nb=5") == {'a': 2, 'b': 5}

def test_pyconfyg():
    pass