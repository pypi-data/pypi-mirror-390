from typing import List, Protocol

from .themes import Theme


class Formatter(Protocol):
    def nums(self, vs: List[int], sep: str = '') -> str:
        raise NotImplementedError

    def num(self, v: int) -> str:
        raise NotImplementedError

    def text(self, s: str) -> str:
        raise NotImplementedError


class ArtFormatter(Formatter):
    def __init__(self, theme: Theme):
        self._theme = theme

    def nums(self, vs: List[int], sep: str = '') -> str:
        return self._theme.render(sep.join(str(v) for v in vs))

    def num(self, v: int) -> str:
        return self.nums([v])

    def text(self, s: str) -> str:
        return self._theme.render(s)


class TextFormatter(Formatter):
    def nums(self, vs: List[int], sep: str = '') -> str:
        return sep.join(str(v) for v in vs)

    def num(self, v: int) -> str:
        return self.nums([v])

    def text(self, s: str) -> str:
        return s
