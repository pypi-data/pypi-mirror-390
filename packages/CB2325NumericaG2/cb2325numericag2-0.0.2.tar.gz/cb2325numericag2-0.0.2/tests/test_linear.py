import pytest

from src.interpolacao import linear

@pytest.mark.parametrize(
    "a, b, t, esperado",
    [
        ([2, 4], [6, 12], 0,   [2.0, 4.0]),
        ([2, 4], [6, 12], 0.5, [4.0, 8.0]),
        ([2, 4], [6, 12], 1,   [6.0, 12.0]),
    ]
)
def test_linear_parametrico(a, b, t, esperado):
    resultado = linear(a, b, t=t)
    assert resultado == esperado

@pytest.mark.parametrize(
    "a, b, x, t, mensagem",
    [
        ([1, 2], [3, 4, 5], None, 0.5, "Os pontos devem ser de mesma dimensão"),
        ([1, 2], [3, 4], None, None, "Algum dos parâmetros deve ser passado"),
        ([1, 2], [3, 4], 2, 0.5, "Apenas um dos parâmetros deve ser passado"),
        ([1, 2, 3], [4, 5, 6], 2, None, "Interpolação por x só é válida para vetores no R2"),
        ([1, 2], [3, 4], None, 1.5, "t deve estar entre 0 e 1"),
        ([1, 2], [3, 4], 5, None, r"x=5 está fora do intervalo \[1, 3\]"),
    ]
)
def test_linear_erros(a, b, x, t, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        linear(a, b, x=x, t=t)
