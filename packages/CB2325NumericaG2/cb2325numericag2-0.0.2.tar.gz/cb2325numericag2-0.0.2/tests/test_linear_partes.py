import pytest

from src.interpolacao import linear_partes

@pytest.mark.parametrize(
    "x_vals, y_vals, x, esperado",
    [
        ([2, 4], [7, 3], 3, 5.0),
        ([1, 3, 5], [2, 6, 10], 1, 2.0),
        ([1, 3, 5], [2, 6, 10], 5, 10.0),
        ([1, 3, 5], [2, 6, 10], 4, 8.0),
        ([5, 1, 3], [10, 2, 6], 2, 4.0),
    ]
)
def test_linear_partes_basico(x_vals, y_vals, x, esperado):
    interpolador = linear_partes(x_vals, y_vals)
    resultado = interpolador(x)
    assert pytest.approx(resultado, rel=1e-9) == esperado


@pytest.mark.parametrize(
    "x_vals, y_vals, x, mensagem",
    [
        ([1, 2, 3], [4, 5], 2, "mesma quantidade de valores de x e y"),
        ([1], [2], 1, "pelo menos dois pontos"),
        ([1, 3, 5], [2, 6, 10], 6, r"x=6 está fora do intervalo \[1, 5\]"),
        ([1, 1, 2], [2, 3, 4], 1.5, "segmento vertical"),
    ]
)
def test_linear_partes_erros(x_vals, y_vals, x, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        interpolador = linear_partes(x_vals, y_vals)
        interpolador(x)