import pytest

from src.aproximacao import minimos_quadrados

def test_minimos_quadrados_recupera_reta_simples():
    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 3.0, 5.0, 7.0]  # y = 2x + 1

    a, b, flag = minimos_quadrados(x, y)

    assert flag == 1
    assert a == pytest.approx(2.0, rel=1e-12, abs=1e-12)
    assert b == pytest.approx(1.0, rel=1e-12, abs=1e-12)


def test_minimos_quadrados_detecta_reta_vertical():
    x = [3.0, 3.0, 3.0, 3.0]
    y = [0.0, 1.0, 2.0, 3.0]

    a, b, flag = minimos_quadrados(x, y)

    assert flag == 0
    assert b == pytest.approx(3.0)
