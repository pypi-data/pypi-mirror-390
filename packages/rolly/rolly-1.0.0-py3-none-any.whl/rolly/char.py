from dataclasses import dataclass
from typing import Dict


@dataclass
class Character:
    _data: Dict

    _abil: Dict[str, int]
    _save: Dict[str, int]

    def __init__(self, path: str):
        with open(path, 'rb') as f:
            import tomllib
            data = tomllib.load(f)

        for sec, data in data:
            match (sec, data):
                case ('abilities', {
                    'str': int(),
                    'dex': int(),
                    'con': int(),
                    'int': int(),
                    'wis': int(),
                    'cha': int(),
                }):
                    for attr in ('str', 'dex', 'con', 'int', 'wis', 'cha'):
                        self._abil[attr] = data[attr]

                case ('saves', {
                    'str': int(),
                    'dex': int(),
                    'con': int(),
                    'int': int(),
                    'wis': int(),
                    'cha': int(),
                }):
                    for attr in ('str', 'dex', 'con', 'int', 'wis', 'cha'):
                        self._save[attr] = data[attr]

                case _:
                    raise RuntimeError(f'invalid character section: {sec}')

    def has_attr(self, attr: str) -> bool:
        return attr in self._abil or attr in self._save

    def abil_val(self, attr: str) -> int:
        if self.has_attr(attr):
            return self._abil[attr]
        return 0

    def save_val(self, attr: str) -> int:
        if self.has_attr(attr):
            return self._save[attr]
        return 0
