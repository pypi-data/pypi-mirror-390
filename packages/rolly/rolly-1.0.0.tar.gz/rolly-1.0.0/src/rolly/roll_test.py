from dataclasses import dataclass
from typing import List

from .roll import Roll


def test_roll():
    r = Roll()
    r._dice.extend([2, 2, 2])
    r1 = r.roll()

    assert len(r1) == 3
    assert r1[0] == 1 or r1[0] == 2
    assert r1[1] == 1 or r1[1] == 2
    assert r1[2] == 1 or r1[2] == 2


@dataclass
class FakeRoller:
    seq: List[int]
    index: int = -1

    def roll(self, bound: int) -> int:
        self.index += 1

        value = self.seq[self.index]
        if value >= bound:
            raise RuntimeError(f"Value {value} exceeds bound {bound}")

        return value


def test_roll_adv():
    r = Roll(roller=FakeRoller([1, 2]).roll)
    r._dice.extend([20])
    r._adv = True
    vs = r.roll()

    assert len(vs) == 1
    assert vs[0] == 2


def test_roll_dis():
    r = Roll(roller=FakeRoller([2, 1]).roll)
    r._dice.extend([20])
    r._dis = True
    vs = r.roll()

    assert len(vs) == 1
    assert vs[0] == 1


def test_parse_dice():
    r = Roll()
    r.parse('d6 d10 d20 d14')

    assert r._dice == [6, 10, 20, 14]


def test_parse_count():
    r = Roll()
    r.parse('d6x3')

    assert r._dice == [6, 6, 6]


def test_parse_adv():
    r = Roll()
    r.parse('d20+')

    assert r._adv


def test_parse_dis():
    r = Roll()
    r.parse('d20-')

    assert r._dis
