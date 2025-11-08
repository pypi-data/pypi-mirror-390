import pytest
from numericals import root

import math

f1 = lambda x: math.sin(x)
f2 = lambda x: math.sqrt(x) - 1


def test_bisection():
    assert root.bisection(f1, 3, 3.2, 2e-8, 10_000) == pytest.approx(math.pi, abs=1e-8)
    assert root.bisection(f2, 0, 2, 2e-8, 10_000) == pytest.approx(1, abs=1e-8)


def test_secant():
    assert root.secant(f1, 2, 4, 2e-8, 10_000) == pytest.approx(math.pi, abs=1e-8)
    assert root.secant(f2, 0, 2, 2e-8, 10_000) == pytest.approx(1, abs=1e-8)