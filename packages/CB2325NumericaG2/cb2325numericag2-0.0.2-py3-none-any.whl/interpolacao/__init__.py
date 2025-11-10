from .linear import interpolacao_linear as linear
from .linear_partes import InterpoladorLinearPartes as linear_partes
from .interpolacao_polinomial import PolinomioInterpolador as polinomial
from .interpolacao_hermite import PolinomioHermite as polinomial_hermite

__all__ = ["linear_partes", "linear", "polinomial", "polinomial_hermite"]
