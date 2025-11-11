from .themes import Theme


TEST_THEME = r'''
H T 0 1 2 3 4 5 6 7 8 9 =
H T 0 1 2 3 4 5 6 7 8 9 =
'''


def test_first_letter():
    t = Theme(TEST_THEME, width=1, padding=1)
    assert t.render('H') == 'H\nH'


def test_last_letter():
    t = Theme(TEST_THEME, width=1, padding=1)
    assert t.render('=') == '=\n='


def test_middle_letter():
    t = Theme(TEST_THEME, width=1, padding=1)
    assert t.render('5') == '5\n5'


def test_space():
    t = Theme(TEST_THEME, width=1, padding=1, space_width=1)
    assert t.render(' ') == ' \n '


def test_multiple_letters():
    t = Theme(TEST_THEME, width=1, padding=1, space_width=2)
    assert t.render('H T') == 'H  T\nH  T'


TEST_THEME_WIDE = r'''
HH TT 00 11 22 33 44 55 66 77 88 99 ==
HH TT 00 11 22 33 44 55 66 77 88 99 ==
'''


def test_wide_theme():
    t = Theme(TEST_THEME_WIDE, width=2, padding=1, space_width=3)
    assert t.render('H') == 'HH\nHH'
    assert t.render('=') == '==\n=='
    assert t.render('5') == '55\n55'
    assert t.render(' ') == '   \n   '
    assert t.render('H T') == 'HH   TT\nHH   TT'


TEST_THEME_VARIED = r'''
HHH TT 00 11 22 33 44 555 66 77 88 99 ===
HHH TT 00 11 22 33 44 555 66 77 88 99 ===
'''


def test_wide_varied():
    t = Theme(TEST_THEME_VARIED, widths={'H': 3, '5': 3, '=': 3}, width=2, padding=1)
    assert t.render('H') == 'HHH\nHHH'
    assert t.render('=') == '===\n==='
    assert t.render('5') == '555\n555'
    assert t.render('H T') == 'HHH  TT\nHHH  TT'
