def test_importable():
    import copydata
    assert hasattr(copydata, "__version__")
