from typing import Sequence
from .linear import interpolacao_linear

class InterpoladorLinearPartes:
    def __init__(
        self, 
        x_valores: Sequence[float],
        y_valores: Sequence[float],
    ):
        self.x = x_valores
        self.y = y_valores


    def __call__(self, t: float):
        if len(self.x) != len(self.y):
            raise ValueError("É necessário ter a mesma quantidade de valores de x e y.")

        if len(self.x) < 2:
            raise ValueError("São necessários pelo menos dois pontos para interpolação linear por partes.")

        pontos = sorted(zip(self.x, self.y), key = lambda p: p[0])
        x_sorted, y_sorted = zip(*pontos)
        for p in pontos:
            if len(p) != 2:
                raise ValueError("Cada ponto deve ter duas coordenadas (x, y).")

            if not (x_sorted[0] <= t <= x_sorted[-1]):
                raise ValueError(f"x={t} está fora do intervalo [{self.x[0]}, {self.x[-1]}].")

            for i in range(len(x_sorted) - 1):
                x0, y0 = x_sorted[i], y_sorted[i]
                x1, y1 = x_sorted[i+1], y_sorted[i+1]
                if x0 == x1:
                    raise ValueError(f'Pontos consecutivos com mesmo x = {x0} geram um segmento vertical: interpolação indefinida.')
                if x0 <= t <= x1:
                    return interpolacao_linear([x0, y0], [x1, y1], x = t)