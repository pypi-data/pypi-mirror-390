import numpy as np
import matplotlib.pyplot as plt

from ..ajuste_polinomial_min_quadrados.ajuste_polinomial_min_quadrados import (
    ajuste_polinomial_min_quadrados,
)


def plot_polinomio_minimos_quadrados(x, y, grau, num_pontos=200):
    """
    Plota os pontos (x, y) e o polinomio ajustado por minimos quadrados.

    Args:
        x (iterable): abscissas.
        y (iterable): ordenadas.
        grau (int): grau desejado do polinomio.
        num_pontos (int): quantidade de pontos na curva ajustada.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    resultado = ajuste_polinomial_min_quadrados(x_arr, y_arr, grau)
    flag_vertical = bool(resultado[-1])

    plt.scatter(x_arr, y_arr, color="royalblue", label="Pontos")

    if flag_vertical:
        x_const = float(resultado[0])
        y_min, y_max = float(y_arr.min()), float(y_arr.max())
        plt.vlines(x_const, y_min, y_max, color="crimson", linewidth=2,
                   label=f"Reta vertical: x = {x_const:.2f}")
        plt.title("Ajuste Polinomial - Reta vertical")
    else:
        coefs = np.asarray(resultado[:-1], dtype=float)
        if x_arr.size == 0:
            raise ValueError("Entrada vazia para o ajuste polinomial.")
        x_min, x_max = float(x_arr.min()), float(x_arr.max())
        x_fit = np.linspace(x_min, x_max, num_pontos)
        y_fit = np.polyval(coefs[::-1], x_fit)
        label = " + ".join(
            [
                f"{coef:.2f}x^{idx}"
                if idx > 0 else f"{coef:.2f}"
                for idx, coef in enumerate(coefs)
            ]
        )
        plt.plot(x_fit, y_fit, color="crimson", linewidth=2,
                 label=f"Ajuste polinomial: {label}")
        plt.title(f"Ajuste Polinomial por Minimos Quadrados (grau {len(coefs) - 1})")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True)
    plt.show()

