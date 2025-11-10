import matplotlib.pyplot as plt
from ..minimos_quadrados.minimos_quadrados import minimos_quadrados

def plot_linear_minimos_quadrados(x, y):
    """
    Plota os pontos fornecidos e a reta de ajuste linear por mínimos quadrados.

    A função calcula os coeficientes da reta que melhor se ajusta aos pontos (x, y)
    usando o método dos mínimos quadrados e plota tanto os pontos originais quanto 
    a reta ajustada. Caso todos os valores de x sejam iguais, plota-se uma reta 
    vertical correspondente.

    Args:
        x (list of float): Lista das abscissas dos pontos a serem plotados.
        y (list of float): Lista das ordenadas dos pontos a serem plotados.

    Returns:
        None
    """
    a, b, c = minimos_quadrados(x, y)

    plt.scatter(x, y, color='royalblue', label='Pontos reais')

    if c == 0:
        # reta vertical
        y_min, y_max = min(y), max(y)
        plt.vlines(b, y_min, y_max, color='crimson', linewidth=2,
                   label=f'Reta vertical: x = {b:.2f}')
        plt.title('Ajuste Linear - Reta Vertical (Mínimos Quadrados)')
    else:
        # reta normal
        x_min, x_max = min(x), max(x)
        x_fit = [x_min, x_max]
        y_fit = [a * x_min + b, a * x_max + b]
        plt.plot(x_fit, y_fit, color='crimson', linewidth=2,
                 label=f'Ajuste: y = {a:.2f}x + {b:.2f}')
        plt.title('Ajuste Linear por mínimos Quadrados')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()
