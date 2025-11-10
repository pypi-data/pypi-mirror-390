import numpy as np
import matplotlib.pyplot as plt
from typing import Callable

def integral_retangulo(func:Callable[[float],float], a: float, b: float, n: int, ponto_corte:float = 0) -> float:
    '''
    Entradas:
    f_string - expressão algébrica
    a - ponto inicial do intervalo
    b - ponto final do intervalo
    n - número de subintervalos da partição
    ponto_corte - parâmetro de altura do subintervalo, recebe:
        - 0 para Soma de Riemann pela Esquerda
        - 1 para Soma de Riemann pela Direita
        - 0.5 para Soma de Riemann pelo Centro

    Saída: Integral aproximada pela Soma de Riemann com método dos retângulos
    '''
    
    variacao = (b - a) / n  
    area = 0

    for i in range(n):
        x_inicio = a + i * variacao
        y_inicio = func(x_inicio)
        x_fim = x_inicio + variacao
        y_fim = func(x_fim)

        x_altura = x_inicio + ponto_corte * (x_fim - x_inicio)
        y_altura = func(x_altura)
       
        area_retangulo = y_altura * variacao
        area += area_retangulo
    return area
    
# Teste unitário

if __name__ == "__main__":
    f = lambda x: np.sin(x)**2
    resultado = integral_retangulo(f, -10, 10, 50, 0)
    print(f"Integral aproximada = {resultado}")

