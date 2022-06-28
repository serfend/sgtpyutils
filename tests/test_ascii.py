from sgtpyutils.ascii import *


def test_case():
    assert is_alpha('a')
    assert is_lower('a')
    assert not is_digit('a')

