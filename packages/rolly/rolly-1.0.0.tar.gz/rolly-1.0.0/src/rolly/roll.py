from dataclasses import dataclass
from secrets import randbelow
from typing import List, Callable

from .char import Character

# A Roller just accepts a maximum value and returns a random
# value in the closed interval [1, max], to simulate rolling
# a die with max sides.
Roller = Callable[[int], int]


def default_roller(bound: int) -> int:
    return randbelow(bound) + 1


@dataclass
class Roll:
    _dice: List[int]
    _roller: Roller
    _adv: bool = False
    _dis: bool = False
    _bonus: int = 0

    def __init__(self, roll: str = '', roller: Roller = default_roller):
        self._dice = []
        self._roller = roller

        if roll != '':
            self.parse(roll)

    @property
    def bonus(self) -> int:
        return self._bonus

    def add_die(self, value: int):
        self._dice.append(value)

    def advantage(self, value: bool):
        self._adv = value

    def disadvantage(self, value: bool):
        self._dis = value

    def roll(self) -> List[int]:
        one = self._roll()

        if self._adv and not self._dis:
            two = self._roll()
            if sum(two) > sum(one):
                return two

        if self._dis and not self._adv:
            two = self._roll()
            if sum(two) < sum(one):
                return two

        return one

    def _roll(self) -> List[int]:
        values = []

        for d in self._dice:
            value = self._roller(d)
            values.append(value)

        return values

    def reset(self):
        self._dice.clear()
        self._adv = False
        self._dis = False
        self._bonus = 0

    def parse(self, roll: str, character: Character | None = None):
        self.reset()

        # Burn whitespace from the ends to handle line endings
        roll = roll.strip()

        attr = ''
        save = False

        while len(roll) > 0:
            if roll.startswith('d'):
                # Reading a die
                roll = roll[1:]

                value = 0
                while len(roll) > 0 and roll[0] in '0123456789':
                    value = value * 10 + int(roll[0])
                    roll = roll[1:]

                self._dice.append(value)
                continue

            if roll.startswith('x'):
                # Reading a count for the previous die
                roll = roll[1:]

                if len(self._dice) == 0:
                    raise RuntimeError('invalid syntax: count found before dice')

                value = 0
                while len(roll) > 0 and roll[0] in '0123456789':
                    value = value * 10 + int(roll[0])
                    roll = roll[1:]

                self._dice.extend([self._dice[-1]] * (value - 1))
                continue

            if roll.startswith('+'):
                # Advantage indicator
                roll = roll[1:]

                self._adv = True
                continue

            if roll.startswith('-'):
                # Disadvantage indicator
                self._dis = True
                roll = roll[1:]
                continue

            if roll.startswith('save'):
                save = True
                roll = roll[4:]
                continue

            if character is not None and len(roll) >= 3 and character.has_attr(roll[:3]):
                attr = roll[:3]
                roll = roll[3:]
                continue

            if roll.startswith(' '):
                # Whitespace is ignored
                roll = roll[1:]
                continue

            # If we didn't hit anything, then we never will, so we bail
            raise RuntimeError(f'invalid syntax: unknown directive ({roll})')

        if attr != '':
            if save:
                self._bonus += character.save_val(attr)
            else:
                self._bonus += character.abil_val(attr)
