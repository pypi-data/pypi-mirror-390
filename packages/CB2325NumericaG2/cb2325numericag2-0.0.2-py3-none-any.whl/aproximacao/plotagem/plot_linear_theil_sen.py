import matplotlib.pyplot as plt
from ..theil_sen.theil_sen import theil_sen

def plot_linear_theil_sen(x, y):
    """
    Plota os pontos (x, y) e a reta de ajuste linear pelo método de Theil-Sen.

    Usa a função theil_sen(x, y) definida anteriormente, que retorna:
      flag, a, b
        - flag = 0 -> reta vertical (todos os x iguais): x = a
        - flag = 1 -> reta não vertical: y = a + b x

    Args:
        x (list[float] | np.ndarray): abscissas
        y (list[float] | np.ndarray): ordenadas
    """
    a, b, flag = theil_sen(x, y)

    # pontos
    plt.scatter(x, y, color='royalblue', label='Pontos reais')

    if flag == 0:
        # reta vertical x = a
        y_min, y_max = min(y), max(y)
        plt.vlines(a, y_min, y_max, color='crimson', linewidth=2,
                   label=f'Reta vertical: x = {a:.2f}')
        plt.title('Ajuste Linear - Reta Vertical (Theil-Sen)')
    else:
        # reta não vertical: y = a + b x
        x_min, x_max = min(x), max(x)
        x_fit = [x_min, x_max]
        y_fit = [a + b * x_min, a + b * x_max]
        plt.plot(x_fit, y_fit, color='crimson', linewidth=2,
                 label=f'Ajuste (Theil-Sen): y = {b:.2f}x + {a:.2f}')
        plt.title('Ajuste Linear por Theil-Sen')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()
