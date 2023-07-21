from sgtpyutils.math import *


def test_sci_num_raw():
    value = 12345678
    result = number_sci(value)
    assert result == '12M345K678'

    result = number_sci_raw_value(value)
    assert result == '12.345M'

