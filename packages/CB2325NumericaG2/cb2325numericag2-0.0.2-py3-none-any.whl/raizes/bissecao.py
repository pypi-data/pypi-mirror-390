from typing import Callable


def bissecao(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-6,
    max_iter: int = 100
) -> float:
    """
    Aplica o método da bisseção para encontrar uma raiz de f(x) = 0 no intervalo [a, b].

    O método assume que f é contínua no intervalo e que f(a) e f(b) possuem sinais opostos,
    garantindo, pelo Teorema do Valor Intermediário, a existência de ao menos uma raiz em [a, b].

    Args:
        f (Callable[[float], float]): Função contínua f(x).
        a (float): Limite inferior do intervalo.
        b (float): Limite superior do intervalo.
        tol (float, opcional): Tolerância para o erro absoluto (critério de parada). Padrão é 1e-6.
        max_iter (int, opcional): Número máximo de iterações. Padrão é 100.

    Returns:
        float: Aproximação da raiz de f(x) = 0 dentro da tolerância especificada.

    Raises:
        TypeError: Se f não for uma função chamável ou se max_iter não for inteiro.
        ValueError: Se tol <= 0, max_iter <= 0 ou f(a) e f(b) não tiverem sinais opostos.
        RuntimeError: Se o método não convergir dentro do número máximo de iterações.
    """
    if not callable(f):
        raise TypeError("O parâmetro f deve ser uma função.")
    if not int(max_iter):
        raise TypeError("O número máximo de iterações deve ser inteiro.")
    if tol <= 0:
        raise ValueError("A tolerância deve ser positiva.")
    if max_iter <= 0:
        raise ValueError("O número máximo de iterações deve ser positivo.")
    if f(a) * f(b) >= 0:
        raise ValueError("f(a) e f(b) devem ter sinais opostos (condição necessária para o método).")
    
    for _ in range(max_iter):
        x_m = (a + b) / 2
        f_m = f(x_m)
        
        if abs(f_m) < tol or (b - a) / 2 < tol:
            return x_m
        
        if f(a) * f_m < 0:
            b = x_m
        else:
            a = x_m
    
    raise RuntimeError("Número máximo de iterações atingido sem convergência.")


if __name__ == "__main__":
    f = lambda x: x**2 - 2
    raiz = bissecao(f, 1, 2)
    print(raiz)
