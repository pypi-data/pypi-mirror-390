from typing import List, Dict, Optional


class Theme:
    _chars: str = 'HT0123456789='

    def __init__(self, templ: str, widths: Optional[Dict[str, int]] = None, padding: int = 0, width: int = 0, space_width: int = 2):
        self._templ: List[str] = templ.split('\n')[1:-1]

        self._height = len(self._templ)
        if self._height == 0:
            raise RuntimeError('invalid theme: no template specified')

        if widths is None:
            self._widths = {}
        else:
            self._widths = widths

        self._pad = padding
        self._width = width
        self._space_width = space_width

        self._validate()

    def render(self, s: str) -> str:
        out_lines = [''] * self._height
        out_str = ''

        # A leading or trailing newline makes things weird
        # and isn't necessary anyway, so drop them
        in_str = s.strip('\n')

        for c in in_str:
            if c == '\n':
                out_str += '\n'.join(out_lines) + '\n'
                out_lines = [''] * self._height
                continue

            if c == ' ':
                for line_index in range(self._height):
                    out_lines[line_index] += ' ' * self._space_width
                continue

            if c not in self._chars:
                raise RuntimeError(f'invalid string: character {c} is not supported')

            offset = self._get_offset(c)
            width = self._get_width(c)
            for line_index in range(self._height):
                out_lines[line_index] += self._templ[line_index][offset:offset + width].ljust(width)

        return out_str + '\n'.join(out_lines)

    def _validate(self):
        self.render(self._chars)

    def _get_offset(self, c: str):
        offset = 0
        ci = self._chars.index(c)

        # Account for everything before the character we want
        for i in range(ci):
            offset += self._get_width(self._chars[i])
            offset += self._pad

        return offset

    def _get_width(self, c: str) -> int:
        w = 0
        if c in self._widths:
            w = self._widths[c]

        if w == 0:
            if self._width == 0:
                raise RuntimeError(f'invalid theme: no width specified for char {c}')
            w = self._width

        return w


DEFAULT = r'''
 ▄▄    ▄▄  ▄▄▄▄▄▄▄▄    ▄▄▄▄      ▄▄▄      ▄▄▄▄▄     ▄▄▄▄▄        ▄▄▄   ▄▄▄▄▄▄▄     ▄▄▄▄    ▄▄▄▄▄▄▄▄    ▄▄▄▄      ▄▄▄▄             
 ██    ██  ▀▀▀██▀▀▀   ██▀▀██    █▀██     █▀▀▀▀██▄  █▀▀▀▀██▄     ▄███   ██▀▀▀▀▀    ██▀▀▀█   ▀▀▀▀▀███  ▄██▀▀██▄  ▄██▀▀██▄           
 ██    ██     ██     ██    ██     ██           ██       ▄██    █▀ ██   ██▄▄▄▄    ██ ▄▄▄        ▄██   ██▄  ▄██  ██    ██  ▄▄▄▄▄▄▄▄ 
 ████████     ██     ██ ██ ██     ██         ▄█▀     █████   ▄█▀  ██   █▀▀▀▀██▄  ███▀▀██▄      ██     ██████   ▀██▄▄███  ▀▀▀▀▀▀▀▀ 
 ██    ██     ██     ██    ██     ██       ▄█▀          ▀██  ████████        ██  ██    ██     ██     ██▀  ▀██    ▀▀▀ ██  ▄▄▄▄▄▄▄▄ 
 ██    ██     ██      ██▄▄██   ▄▄▄██▄▄▄  ▄██▄▄▄▄▄  █▄▄▄▄██▀       ██   █▄▄▄▄██▀  ▀██▄▄██▀    ██      ▀██▄▄██▀   █▄▄▄██   ▀▀▀▀▀▀▀▀ 
 ▀▀    ▀▀     ▀▀       ▀▀▀▀    ▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀   ▀▀▀▀▀         ▀▀    ▀▀▀▀▀      ▀▀▀▀     ▀▀         ▀▀▀▀      ▀▀▀▀             
'''

ALPHA = r'''
 H  H     TTTTTT      000       11       22      333      4  4     5555       6       77777      888       9999         
 H  H       TT       0  00     111      2  2        3     4  4     5         6           7      8   8     9   9     === 
 HHHH       TT       0 0 0      11        2       33      4444     555      6666        7        888       9999         
 H  H       TT       00  0      11       2          3        4        5     6   6       7       8   8        9      === 
 H  H       TT        000      1111     2222     333         4     555       666        7        888        9           
'''

OUTLINE = r'''
 _    _   _______    ___    __   ___    ____    _  _     _____     __    ______    ___     ___           
| |  | | |__   __|  / _ \  /_ | |__ \  |___ \  | || |   | ____|   / /   |____  |  / _ \   / _ \   ______ 
| |__| |    | |    | | | |  | |    ) |   __) | | || |_  | |__    / /_       / /  | (_) | | (_) | |______|
|  __  |    | |    | | | |  | |   / /   |__ <  |__   _| |___ \  | '_ \     / /    > _ <   \__, |  ______ 
| |  | |    | |    | |_| |  | |  / /_   ___) |    | |    ___) | | (_) |   / /    | (_) |    / /  |______|
|_|  |_|    |_|     \___/   |_| |____| |____/     |_|   |____/   \___/   /_/      \___/    /_/           
'''


ALL_THEMES: Dict[str, Theme] = {
    'default': Theme(DEFAULT, width=10, space_width=8),
    'alpha': Theme(ALPHA, {
        'T': 8,
        '0': 7,
        '6': 7,
        '7': 7,
        '8': 7,
        '9': 7,
        '=': 5,
    }, width=6, padding=3, space_width=5),
    'outline': Theme(OUTLINE, {
        'H': 8,
        'T': 9,
        '1': 4,
        '2': 6,
        '4': 8,
        '7': 8,
        '=': 8,
    }, width=7, padding=1, space_width=3)
}


def get_themes() -> List[str]:
    return list(ALL_THEMES.keys())


def get_theme(name: str) -> Theme:
    key = name.strip().lower()
    if key in ALL_THEMES:
        return ALL_THEMES[key]

    raise RuntimeError(f'invalid theme name: {name}')
