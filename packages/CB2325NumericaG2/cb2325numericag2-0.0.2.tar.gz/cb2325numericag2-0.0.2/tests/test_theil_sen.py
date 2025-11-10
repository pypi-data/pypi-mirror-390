import pytest

from src.aproximacao import theil_sen

def test_theil_sen_recupera_reta_simples():
    x = [0.0, 1.0, 2.0, 3.0, 4.0]
    y = [1.0, 3.0, 5.0, 7.0, 9.0]  # y = 2x + 1

    a, b, flag = theil_sen(x, y)

    assert flag == 1
    assert b == pytest.approx(2.0, rel=1e-12, abs=1e-12)  # inclinacao
    assert a == pytest.approx(1.0, rel=1e-12, abs=1e-12)  # intercepto


def test_theil_sen_detecta_reta_vertical():
    x = [4.0, 4.0, 4.0, 4.0]
    y = [0.0, 2.0, 4.0, 6.0]

    a, b, flag = theil_sen(x, y)

    assert flag == 0
    assert a == pytest.approx(4.0)
    assert b == pytest.approx(4.0)


def test_theil_sen_rejeita_listas_de_tamanhos_diferentes():
    with pytest.raises(ValueError):
        theil_sen([0.0, 1.0], [2.0])
