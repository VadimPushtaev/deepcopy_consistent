import pytest

from thread_safe_dict import ThreadSafeDict


def test_iter():
    d = ThreadSafeDict({1: 1, 2: 2, 3: 3})

    it1 = iter(d.items())
    assert next(it1) == (1, 1)

    it2 = iter(d.items())
    assert next(it2) == (1, 1)

    d[2] = "ONLY FOR it3"
    it3 = iter(d.items())
    assert next(it3) == (2, "ONLY FOR it3")  # higher layer

    assert next(it1) == (2, 2)
    assert next(it1) == (3, 3)
    with pytest.raises(StopIteration):
        next(it1)

    assert next(it2) == (2, 2)
    assert next(it2) == (3, 3)
    with pytest.raises(StopIteration):
        next(it2)

    assert next(it3) == (1, 1)
    assert next(it3) == (3, 3)
    with pytest.raises(StopIteration):
        next(it3)


def test_iter__new_keys():
    d = ThreadSafeDict({1: 1, 2: 2, 3: 3})

    it1 = iter(d.items())
    assert next(it1) == (1, 1)

    d[4] = 4

    assert next(it1) == (2, 2)
    assert next(it1) == (3, 3)
    with pytest.raises(StopIteration):
        next(it1)


def test_iter__del():
    d = ThreadSafeDict({1: 1, 2: 2, 3: 3})

    it1 = iter(d.items())
    assert next(it1) == (1, 1)

    del d[2]
    assert d.get(2) is None
    print(d._layers)


def test_iter__get():
    d = ThreadSafeDict({1: 1, 2: 2, 3: 3})

    assert d[2] == 2

    it1 = iter(d.items())
    assert next(it1) == (1, 1)

    d[2] = 'a'
    assert d[2] == 'a'

    assert next(it1) == (2, 2)
    assert next(it1) == (3, 3)
    with pytest.raises(StopIteration):
        next(it1)

    assert d[2] == 'a'