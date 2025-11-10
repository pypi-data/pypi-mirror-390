from typing import Callable, Optional


def newton_raphson(
    f: Callable[[float], float],
    x0: float,
    tol: float = 1e-6,
    max_iter: int = 100,
    df: Optional[Callable[[float], float]] = None
) -> float:
    """
    Aplica o método de Newton-Raphson para encontrar uma raiz de f(x) = 0.

    O método itera a partir de uma aproximação inicial x0 até que a diferença
    entre iterações consecutivas seja menor que a tolerância especificada.

    Args:
        f (Callable[[float], float]): Função f(x) cuja raiz será encontrada.
        x0 (float): Aproximação inicial para a raiz.
        tol (float, opcional): Tolerância para o erro absoluto (critério de parada).
        max_iter (int, opcional): Número máximo de iterações permitidas.
        df (Optional[Callable[[float], float]], opcional): Derivada de f(x).
            Se None, a derivada será aproximada numericamente por diferenças centrais.

    Returns:
        float: Aproximação da raiz de f(x) = 0.

    Raises:
        TypeError: Se f não for uma função chamável ou se max_iter não for inteiro.
        ValueError: Se tol <= 0 ou max_iter <= 0.
        ZeroDivisionError: Se a derivada for nula em algum ponto.
        RuntimeError: Se o método não convergir dentro do limite de iterações.
    """

    if not callable(f):
        raise TypeError("O parâmetro f deve ser uma função.")
    if not int(max_iter):
        raise TypeError("O número máximo de iterações deve ser inteiro.")
    if tol <= 0:
        raise ValueError("A tolerância deve ser positiva.")
    if max_iter <= 0:
        raise ValueError("O número máximo de iterações deve ser positivo.")

    # Derivada numérica (se não fornecida)
    if df is None:
        def df(x: float, h: float = 1e-6) -> float:
            return (f(x + h) - f(x - h)) / (2 * h)

    for _ in range(max_iter):
        f_x = f(x0)
        df_x = df(x0)

        if df_x == 0:
            raise ZeroDivisionError(f"Derivada nula — método falha em x = {x0:.6f}")

        x1 = x0 - f_x / df_x

        if abs(x1 - x0) < tol:
            return x1

        x0 = x1

    raise RuntimeError("Número máximo de iterações atingido sem convergência.")


if __name__ == "__main__":
    f = lambda x: x**2 - 2
    df = lambda x: 2 * x
    raiz = newton_raphson(f, 1, df=df)
    print(raiz)
