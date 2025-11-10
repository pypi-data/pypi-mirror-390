import numpy as np

def theil_sen(x: list, y: list) -> tuple:
    """
    Estima y = a + b x (Theil-Sen).
    Retorna: flag, a, b
      - flag = 0 -> reta vertical (todos x iguais): x = a
      - flag = 1 -> reta nǜo vertical: y = a + b x
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    if x.shape != y.shape:
        raise ValueError("x e y devem ter o mesmo tamanho.")
    n = x.size
    if n < 2:
        raise ValueError("é preciso ao menos dois pontos.")

    # Caso vertical: todos os x iguais
    if np.ptp(x) == 0.0:  # ptp = max(x) - min(x)
        x0 = float(np.median(x))
        return x0, x[0], 0

    # Caso geral: ignora pares com dx == 0
    slopes = []
    for i in range(n - 1):
        dx = x[i+1:] - x[i]
        valid = dx != 0
        if np.any(valid):
            dy = y[i+1:] - y[i]
            slopes.extend((dy[valid] / dx[valid]).tolist())

    b = float(np.median(slopes))       # inclinação = mediana das inclinações
    a = float(np.median(y - b * x))    # intercepto = mediana dos resíduos
    return a, b, 1

