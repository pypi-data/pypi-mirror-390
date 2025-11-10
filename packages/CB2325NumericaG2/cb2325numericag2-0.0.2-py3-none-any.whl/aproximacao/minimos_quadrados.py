def minimos_quadrados(vetor_x : list,vetor_y : list) -> tuple:
    """
    Método de aproximação por minimos quadrados.  
    Retorna os coeficientes c, a e b da reta cy = ax + b
    a = numerador/denominador
    b = f(a)

    Args:
        vetor_x (list of float): Lista das abscissas.
        vetor_y (list of float): Lista das ordenadas.

    Returns:
        tuple:
            c (int): Indicador do tipo de reta. 
                     1 -> reta normal (y = a*x + b), 
                     0 -> reta vertical (x = b)
            a (float): Coeficiente angular da reta
            b (float): Coeficiente linear da reta 
    
    """
    #calculo do Denominador de a 
    somatorio_xi = 0
    somatorio_xi_ao_quadrado = 0
    for xi in vetor_x:
        somatorio_xi += xi
        somatorio_xi_ao_quadrado += xi**2
    n = len(vetor_x)
    denominador = (n*somatorio_xi_ao_quadrado) - (somatorio_xi**2)
    if denominador != 0:
        #calculo do numerador de a
        somatorio_xi_yi = 0
        somatorio_yi = 0
        for i in range(0,n):
            somatorio_yi += vetor_y[i]
            somatorio_xi_yi += vetor_x[i]*vetor_y[i]
        numerador = (n*somatorio_xi_yi) - (somatorio_xi*somatorio_yi)

        #calculo final de a
        a = numerador/denominador

        #calculo de b
        b = (somatorio_yi - a*somatorio_xi)/n

        return a, b, 1
    else: # Todos os x são iguais => Reta vertical 
        return 1, vetor_x[0], 0

