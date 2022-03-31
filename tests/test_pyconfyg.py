from pyconfyg import GridConfyg, Confyg, parse_strings

def test_parse_strings_single():
    assert parse_strings("a=2") == {'a': 2}

def test_parse_strings_multiple():
    assert parse_strings("a=2", "b=4") == {'a': 2, 'b': 4}

def test_parse_strings_with_env():
    env = {'c': 3}
    assert parse_strings("a=2", "b=4", env=env) == {'a': 2, 'b': 4, 'c': 3}

def test_parse_strings_with_env_overwritten():
    env = {'c': 3}
    assert parse_strings("c=10", env=env) == {'c': 10}

def test_parse_strings4():
    assert parse_strings("a=2\nb=5") == {'a': 2, 'b': 5}

def test_confyg():
    c = Confyg("a=2\nb=5")
    assert c.dict == {'a': 2, 'b': 5}
    assert c.string == "\na = 2\nb = 5\n"

def test_confyg_with_overwrite():
    c = Confyg("a=2\nb=5", {'b': 2})
    assert c.dict == {'a': 2, 'b': 2}
    assert c.string == "\na = 2\nb = 2\n"

def test_confyg_with_unoverwritten():
    c = Confyg("a=2\nb=5", {'c': 2})
    assert c.dict == {'a': 2, 'b': 5, 'c': 2}
    assert c.string == "\na = 2\nb = 5\nc = 2\n"

def test_gridconfyg():
    gc = GridConfyg("a=2\nb=5", {'b': [1,2]})
    assert [c.dict for k,c in iter(gc)] == [{'a': 2, 'b': 1}, {'a': 2, 'b': 2}]
