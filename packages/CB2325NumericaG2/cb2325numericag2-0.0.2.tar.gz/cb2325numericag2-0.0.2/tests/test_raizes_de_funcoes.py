import pytest
import math

from src.raizes import metodo_bisseccao, metodo_newton_raphson, metodo_secante

def test_metodo_bisseccao():
    f = lambda x: x**2 - 2
    aproximacao = metodo_bisseccao(f, 1, 2, tol=1e-7, max_iter=100)
    assert abs(aproximacao - math.sqrt(2)) < 1e-7

def test_metodo_newton_raphson():
    f = lambda x: x**2 - 2
    df = lambda x: 2*x
    aproximacao = metodo_newton_raphson(f, x0=1, tol=1e-7, max_iter=100, df=df)
    assert abs(aproximacao - math.sqrt(2)) < 1e-7

def test_metodo_secante():
    f = lambda x: x**2 - 2
    aproximacao = metodo_secante(f, x0=1, x1=2, tol=1e-7, max_iter=100)
    assert abs(aproximacao - math.sqrt(2)) < 1e-7


if __name__ == "__main__":
    pytest.main()
