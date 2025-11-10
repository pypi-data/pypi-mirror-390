import pytest

from src.aproximacao import ajuste_polinomial_min_quadrados

def test_ajuste_polinomial_min_quadrados_recupera_reta():
    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 3.0, 5.0, 7.0]  # y = 2x + 1

    resultado = ajuste_polinomial_min_quadrados(x, y, grau=1)

    coefs = resultado[:-1]
    flag = bool(resultado[-1])

    assert flag is False
    assert coefs[0] == pytest.approx(1.0, rel=1e-12, abs=1e-12)
    assert coefs[1] == pytest.approx(2.0, rel=1e-12, abs=1e-12)


def test_ajuste_polinomial_min_quadrados_reduz_grau_quando_necessario():
    x = [0.0, 1.0, 2.0]
    y = [1.0, 4.0, 9.0]  # se ajustado com grau alto, deve reduzir para 2

    resultado = ajuste_polinomial_min_quadrados(x, y, grau=5)

    # 3 coeficientes + flag final
    assert len(resultado) == 4
    assert bool(resultado[-1]) is False


def test_ajuste_polinomial_min_quadrados_detecta_reta_vertical():
    x = [2.0, 2.0, 2.0]
    y = [0.0, 1.0, 2.0]

    resultado = ajuste_polinomial_min_quadrados(x, y, grau=2)

    assert len(resultado) == 2
    assert resultado[0] == pytest.approx(2.0)
    assert bool(resultado[1]) is True


def test_ajuste_polinomial_min_quadrados_valida_dimensoes():
    with pytest.raises(ValueError):
        ajuste_polinomial_min_quadrados([0.0, 1.0], [2.0], grau=1)
