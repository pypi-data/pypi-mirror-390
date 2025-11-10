def erro_relativo(valor_real: float, valor_aproximado: float) -> float:
    """Calcula o erro do valor aproximado em proporção ao valor real.
    Retornando a divisão entre a diferença dos valores pelo valor real, em módulo.

    Args:
        valor_real(Float) = valor inicial com varias casas iniciais
        valor_aproximado(Float) = arrendondamento do valor real

    Returns:
        float: erro relativo com até sete casas decimais
    """

    erro_relativo = (valor_real - valor_aproximado) / valor_real

    if erro_relativo < 0:
        return round(-erro_relativo, 7)
    else:
        return round(erro_relativo, 7)
