from src.vector_clock import VectorClock
from src.versioned_kv import VersionedKV


def _vc(vec):
    v = VectorClock(len(vec))
    v.vector = list(vec)
    return v


def test_merge_sum_resolves_conflict():
    kv = VersionedKV(3)
    kv.put('x', 0, _vc([0, 0, 0]), strategy='merge')
    kv.put('x', 1, _vc([1, 0, 0]), strategy='merge')
    value, vc, status = kv.put('x', 0, _vc([0, 1, 0]), strategy='merge')
    assert status == "conflict resolved by merge"
    assert value == 1                     # 1 + 0
    assert vc.vector == [1, 1, 0]


def test_merge_string_concatenation():
    kv = VersionedKV(3)
    kv.put('s', "a", _vc([0, 0, 0]), strategy='merge')
    kv.put('s', "b", _vc([1, 0, 0]), strategy='merge')
    value, _, status = kv.put('s', "c", _vc([0, 1, 0]), strategy='merge')
    assert status == "conflict resolved by merge"
    assert value == "b|c"


def test_lww_takes_last():
    kv = VersionedKV(3)
    kv.put('x', 0, _vc([0, 0, 0]), strategy='lww')
    kv.put('x', 1, _vc([1, 0, 0]), strategy='lww')
    value, _, status = kv.put('x', 0, _vc([0, 1, 0]), strategy='lww')
    assert status == "conflict resolved by LWW"
    assert value == 0


def test_older_update_ignored():
    kv = VersionedKV(3)
    kv.put('x', 0, _vc([0, 0, 0]), strategy='merge')
    kv.put('x', 5, _vc([2, 1, 0]), strategy='merge')
    value, _, status = kv.put('x', 9, _vc([1, 0, 0]), strategy='merge')
    assert status == "ignored (older)"
    assert value == 5