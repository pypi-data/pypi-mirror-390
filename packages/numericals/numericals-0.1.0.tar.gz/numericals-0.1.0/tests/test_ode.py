import pytest
from numericals import ode

import math

f1 = lambda x, y: y


def test_euler():

    f1_table = ode.euler(f1, 0, 1, 1, 10_000)

    assert f1_table[0][1] == 1
    assert f1_table[-1][1] == pytest.approx(math.e, abs=1e-3)
