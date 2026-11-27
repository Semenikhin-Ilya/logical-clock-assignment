from src.lamport_clock import LamportClock


def test_initial_value():
    assert LamportClock().value == 0


def test_increment():
    c = LamportClock()
    assert c.increment() == 1
    assert c.increment() == 2


def test_update_uses_max_plus_one():
    c = LamportClock()
    c.increment(); c.increment()          # value = 2
    assert c.update(5) == 6               # max(2,5)+1
    assert c.update(1) == 7               # max(6,1)+1


def test_causality_preserved():
    c1, c2 = LamportClock(), LamportClock()
    c1.increment()                        # 1
    sent = c1.increment()                 # 2 (отправка)
    received = c2.update(sent)            # 3 (приём)
    assert received > sent