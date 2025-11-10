from typing import Callable, TypeAlias

FuncaoReal: TypeAlias = Callable[[float], float]

from typing import Callable

def secante(f: Callable[[float], float], x0: float, x1: float, tol=1e-6, max_iter=100) -> float:
    """
    Encontra uma raiz da função f usando o método da secante.

    O método da secante é um método numérico para encontrar raízes de funções que utiliza
    uma aproximação linear baseada em dois pontos iniciais.

    Args:
        f (Callable[[float], float]): A função f(x) para qual se deseja encontra raiz.
        x0 (float): O primeiro ponto inicial.
        x1 (float): O segundo ponto inicial.
        tol (float): A tolerância para o critério de parada.
        max_iter (int): O número máximo de interações permitidas.
    
    Returns:
        float: Aproximação da raiz da função f(x).
    
    Raises:
        ValueError: Se o número máximo de iterações for atingido sem convergência.
        ZeroDivisionError: Se a diferença entre f(x1) e f(x0) for muito pequena.
    """

    for _ in range(max_iter):
        if abs(f(x1) - f(x0)) < 1e-12:
            raise ZeroDivisionError("Diferença muito pequena")
        x2 = x1 - f(x1)*(x1 - x0)/(f(x1) - f(x0))
        if abs(x2 - x1) < tol:
            return x2
        x0, x1 = x1, x2
    raise ValueError("Número máximo de iterações atingido")

if __name__ == "__main__":
    f = lambda x: x**2 - 2
    raiz = secante(f, 1, 2)
    print(raiz)
