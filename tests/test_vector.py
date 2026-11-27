from src.vector_clock import VectorClock, happens_before, concurrent


def test_increment():
    vc = VectorClock(3)
    vc.increment(0)
    vc.increment(0)
    vc.increment(1)
    assert vc.vector == [2, 1, 0]


def test_update_componentwise_max():
    a = VectorClock(3); a.vector = [1, 2, 0]
    b = VectorClock(3); b.vector = [3, 0, 1]
    a.update(b)
    assert a.vector == [3, 2, 1]


def test_copy_is_independent():
    a = VectorClock(3); a.vector = [1, 0, 0]
    b = a.copy()
    b.increment(1)
    assert a.vector == [1, 0, 0]
    assert b.vector == [1, 1, 0]


def test_happens_before():
    a = VectorClock(3); a.vector = [1, 0, 0]
    b = VectorClock(3); b.vector = [2, 1, 0]
    assert happens_before(a, b)
    assert not happens_before(b, a)
    assert not happens_before(a, a)       # рефлексивность не считается «до»


def test_concurrent():
    a = VectorClock(3); a.vector = [1, 0, 0]
    b = VectorClock(3); b.vector = [0, 1, 0]
    assert concurrent(a, b)
    assert not happens_before(a, b)
    assert not happens_before(b, a)