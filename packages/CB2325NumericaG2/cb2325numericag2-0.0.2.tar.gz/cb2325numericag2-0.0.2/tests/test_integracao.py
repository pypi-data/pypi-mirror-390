import pytest
import numpy as np

from src.integracao import integral_trapezio, integral_componentes, integral_retangulo

# ---------- TESTES DE FUNCIONALIDADE ----------

def test_integral_regra_trapezio():
    """Verifica se a integral de sin²(x) em [0, π] ≈ π/2"""
    f = lambda x: np.sin(x)**2
    result = integral_trapezio(f, 0, np.pi, 100)
    expected = np.pi / 2
    assert np.isclose(result, expected, atol=1e-3)

def test_integral_regra_retangulo():
    """Verifica se a integral de sin²(x) em [0, π] ≈ π/2"""
    f = lambda x: np.sin(x)**2
    result = integral_retangulo(f, 0, np.pi, 100, 0)
    expected = np.pi / 2
    assert np.isclose(result, expected, atol=1e-3)


def test_integracao_componentes_funcao_vetorial():
    """
    Testa se a integração de uma função vetorial simples f(t) = (t, t^2, t^3)
    em [0, 1] é próximo de (1/2, 1/3, 1/4)
    """

    f = lambda t: (t, t**2, t**3)

    resultado = integral_componentes(f, 0, 1, 1000, 0.5)
    esperado = (1/2, 1/3, 1/4)

    # compara cada componente com tolerância
    for r, e in zip(resultado, esperado):
        assert np.isclose(r, e, rtol=1e-3, atol=1e-3), (
            f"Componente incorreta: esperado {e}, obtido {r}"
        )

# ---------- TESTES DE ERROS E TIPOS ----------

# ----------  Método dos Trapézios ---------- 

def test_tipo_errado_func():
    """Erro se 'func' não for chamável"""
    with pytest.raises(TypeError):
        integral_trapezio(123, 0, 1, 10)

def test_tipo_errado_pi_pf():
    """Erro se pi/pf não forem floats"""
    with pytest.raises(TypeError):
        integral_trapezio(lambda x: x, "a", 2, 10)

def test_tipo_errado_n():
    """Erro se n não for inteiro"""
    with pytest.raises(TypeError):
        integral_trapezio(lambda x: x, 0, 1, 2.5)

# ----------  Método dos Retângulos ---------- 
       
def test_tipo_errado_func2():
    """Erro se 'func' não for chamável"""
    with pytest.raises(TypeError):
        integral_retangulo(123, 0, 1, 10)

def test_tipo_errado_pi_pf2():
    """Erro se pi/pf não forem floats"""
    with pytest.raises(TypeError):
        integral_retangulo(lambda x: x, "a", 2, 10)

def test_tipo_errado_n2():
    """Erro se n não for inteiro"""
    with pytest.raises(TypeError):
        integral_retangulo(lambda x: x, 0, 1, 2.5)
        
# ----------  Integração de função vetorial ---------- 

def test_erro_tipo_saida_funcao():
    """Deve gerar TypeError se a função não retornar tupla/lista"""
    f = lambda x: x**2  # não retorna tupla!

    with pytest.raises(TypeError):
        integral_componentes(f, 0, 1, 10, 0.5)

def test_erro_parametros_invalidos():
    """Deve gerar erro se o número de subintervalos for inválido"""
    def f(t):
        return (t, t**2)

    with pytest.raises(ZeroDivisionError):
        integral_componentes(f, 0, 1, 0, 0.5)

def test_tipo_errado_parametros():
    """Erro se parâmetros a, b ou ponto_corte não forem numéricos"""
    def f(t):
        return (t, t**2)

    with pytest.raises(TypeError):
        integral_componentes(f, "0", 1, 10, 0.5)

    with pytest.raises(TypeError):
        integral_componentes(f, 0, 1, 10, "meio")

