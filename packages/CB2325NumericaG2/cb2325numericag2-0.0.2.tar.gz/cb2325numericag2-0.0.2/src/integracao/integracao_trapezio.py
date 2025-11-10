import numpy as np
from functools import reduce
from typing import Callable

def integral_trapezio(func:Callable[[float],float], pi:float, pf:float, n:int) -> float:
    """
    Aplica o método da Regra do Trapézio Composta para encontrar uma aproximação da integral de f(x) 
    no intervalo [pi, pf]. Para isso, o intervalo é dividido em n subintervalos de tamanho igual e em cada 
    um deles é construído um trapézio que aproximará a área sob o gráfico de f(x) naquela parte.

    Args:
        func (Callable[[float], float]): Função f(x).
        pi (float): Limite inferior do intervalo.
        pf (float): Limite superior do intervalo.
        n (int): Número de subdivisões trapezoidais.

    Returns:
        float: Aproximação da integral de f(x) = 0.

    Raises:
        TypeError: Se um dos seguintes casos ocorrer:
            - func não for uma função chamável 
            - pi e pf não forem float 
            - n não for inteiro  
        ZeroDivisionError: n = 0
    """
    if not callable(func):
        raise TypeError("'func' deve ser uma função chamável")
    if not isinstance(pi, (int, float)) or not isinstance(pf, (int, float)):
        raise TypeError("'pi' e 'pf' devem ser números (int ou float)")
    if not isinstance(n, int):
        raise TypeError("'n' deve ser um inteiro")
    if n == 0:
        raise ZeroDivisionError("'n' deve ser um inteiro diferente de 0")
    if n < 0:
        return None
    h = (pf - pi) / n
    pontos = [pi + h*i for i in range(n+1)]
    
    # Cálculo da integral com regra do trapézio
    area = reduce(lambda acc, i: acc + (func(pontos[i]) + func(pontos[i+1])) * h / 2, range(n), 0)
    return area

# Teste unitário

if __name__ == "__main__":
    f = lambda x: np.sin(x)**2
    resultado = integral_trapezio(f, -10, 10, -100)
    print(f"Integral aproximada = {resultado}")
