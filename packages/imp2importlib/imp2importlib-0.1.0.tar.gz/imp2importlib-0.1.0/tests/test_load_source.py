from imp import load_source


def test_load_source():
    assert callable(load_source)
    module = load_source("imp", "src/imp/__init__.py")
    assert module.load_source.__code__ == load_source.__code__
    assert module.load_source.__name__ == load_source.__name__
