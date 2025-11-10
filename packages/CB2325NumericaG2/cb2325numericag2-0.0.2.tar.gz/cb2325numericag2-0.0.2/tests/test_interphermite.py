import pytest
import numpy as np
from src.interpolacao import polinomial_hermite

# ---------- TESTES DOS COEFICIENTES ----------
# @pytest.mark.parametrize(
#     "dados, esperado",
#     [
#         ([(0, 1, 2),(1, 2, 3)],[1.0, 2.0, 1.0]),
#         ([(0, 0, 1),(1, 1, 2)],[0.0, 1.0, 0.0]),
#         ([(1, 1, 0)],[1.0]),
#         ([(0, 1, 0, -1)],[1.0, 0.0, -0.5]),
#         ([(0, 0, 1),(2, 4, 3)], [0.0, 1.0, 0.25]),
#         ([(-2,-12,22),(1,9,10)],[2.0, 1.0, 2.0, 4.0]),
#         ([(-1,2,-8,56),(0,1,0,0),(1,2,8,56)],[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
#     ]
# )
# def test_coeficientes_hermite(dados, esperado):
#     resultado = polinomial_hermite(dados)
#     assert np.allclose(resultado.__repr__(), esperado, atol=1e-6)

# # ---------- TESTES DE AVALIAÇÃO ----------
# @pytest.mark.parametrize(
#     "dados, x, esperado",
#     [
#         ([ (0, 1, 2), (1, 2, 3) ], 0.5, 1.625),
#         ([ (0, 0, 1), (1, 1, 2) ], 2, 4.0),
#         ([ (1, 1, 0) ], 10, 1.0),
#         ([ (0, 1, 0, -1) ], 2, 1 - 2**2/2),
#         ([ (0, 0, 1), (2, 4, 3) ], 1, 1.625),
#     ]
# )
# def test_avaliar_hermite(dados, x, esperado):
#     resultado = polinomial_hermite(dados)
#     assert resultado(x) == pytest.approx(esperado, abs=1e-6)

# @pytest.mark.parametrize(
#     "dados, xs, esperados",
#     [
#         ([ (0, 1, 2), (1, 2, 3) ], [0, 1], [1.0, 2.0]),
#         ([ (0, 0, 1), (1, 1, 2) ], [0, 2], [0.0, 4.0]),
#         ([ (1, 1, 0) ], [0, 1, 2], [1.0, 1.0, 1.0]),
#         ([ (0, 1, 0, -1) ], [0, 2], [1.0, -1.0]),
#     ]
# )
# def test_lista_novos_pontos_hermite(dados, xs, esperados):
#     resultado = polinomial_hermite(dados)
#     assert np.allclose(resultado(xs), esperados, atol=1e-6)

# # ---------- TESTES DE ERROS ----------

# def test_erro_sem_dados():
#     with pytest.raises(ValueError):
#         polinomial_hermite([])

# def test_erro_tupla_invalida():
#     with pytest.raises(ValueError):
#         polinomial_hermite([(1,)])

# def test_erro_tipo_invalido_call():
#     p = polinomial_hermite([(0, 1, 2)])
#     with pytest.raises(ValueError):
#         p("texto")

def test_erro_tipo_invalido_call():
    p = polinomial_hermite([(0, 1, 2)])
    with pytest.raises(ValueError):
        p([0, "a", 2])
