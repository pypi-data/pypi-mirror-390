import numpy as np

def ajuste_polinomial_min_quadrados(x: list[float], y: list[float], grau: int, cond_thresh=1e12) -> np.ndarray:
    """
    Método de aproximação polinomial por mínimos quadrados.  
    Retorna os coeficientes do polinômio de melhor ajuste aos pontos (x, y),
    determinado pelo grau especificado, utilizando o método dos mínimos quadrados.

    A função ajusta automaticamente o grau se houver menos pontos do que
    coeficientes possíveis, e verifica condições de instabilidade numérica
    baseadas no posto da matriz de Vandermonde.

    Args:
        x (list of float): Lista das abscissas.
        y (list of float): Lista das ordenadas.
        grau (int): Grau do polinômio desejado para o ajuste.
        cond_thresh (float, opcional): Limiar para o número de condição usado
            na verificação de estabilidade numérica (padrão: 1e12).

    Returns:
        numpy.ndarray:
            Vetor contendo os coeficientes do polinômio ajustado na forma:
                [a₀, a₁, a₂, ..., aₙ, flag_vertical]
            onde:
                a₀, a₁, ..., aₙ são os coeficientes do polinômio
                flag_vertical (bool): 
                    True  → caso de reta vertical (x constante)
                    False → ajuste polinomial normal
    """
    
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    # Vamos criar uma matriz (n x m)
    # n é o grau do polinômio 
    # m é o número de coordenadas que o usuário utilizar

    m = len(x)
    
    if m != len(y): 
        # O usuário errou ao enviar dados para a função.
        raise ValueError(f"len(x)={m} diferente de len(y)={len(y)}")
    
    # Teste direto de reta vertical
    if np.allclose(x, x[0]):
        # Todos os valores de x são iguais → reta vertical
        return np.array([x[0], True], dtype=object)
    
    # Reduz o grau se houver menos pontos que coeficientes
    if m < grau + 1:
        return ajuste_polinomial_min_quadrados(x, y, m - 1, cond_thresh)
    
    # Matriz de Vandermonde
    X = np.vander(x, grau + 1, increasing=True)
    
    # Número máximo de colunas linearmente independentes
    sigma = np.linalg.svd(X, compute_uv=False)
    # Tolerância baseada no condicionamento numérico
    _tol = sigma[0] / cond_thresh
    rank = np.linalg.matrix_rank(X, tol=_tol)
    
    # Ajusta o grau com base no posto da matriz
    if rank < X.shape[1]:
        X = np.vander(x, rank, increasing=True)
    
    # Lista dos coeficientes do polinômio via mínimos quadrados diretos
    a = np.linalg.inv(X.T @ X) @ X.T @ y

    # O último valor do array indica se a função é uma reta vertical
    a = np.append(a, False)

    return a
