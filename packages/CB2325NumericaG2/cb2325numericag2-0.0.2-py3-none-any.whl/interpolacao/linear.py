from typing import Optional, TypeAlias

Vetor: TypeAlias = list[float]

def interpolacao_linear(
    a: Vetor,
    b: Vetor,
    x:Optional[float] = None,
    t:Optional[float] = None
    ) -> float | Vetor:
    """
    Realiza interpolação linear entre dois pontos em Rⁿ.

    A método permite dois modos de uso:
        - Modo cartesiano (R²): o usuário fornece um valor 'x' intermediário entre
        as abscissas de 'a' e 'b', e a função retorna o valor interpolado de 'y';
        - Modo paramétrico (Rⁿ): o usuário fornece um parâmetro 't' ∈ [0, 1],
        e a função retorna o ponto interpolado entre 'a' e 'b' em qualquer dimensão.

    Args:
        a : list[float]
            Primeiro ponto (vetor em Rⁿ).
        b : list[float]
            Segundo ponto (mesma dimensão de 'a').
        x : float, optional
            Valor da variável independente (somente em R²). Deve estar dentro
            do intervalo [xₐ, x_b].
        t : float, optional
            Parâmetro de interpolação ∈ [0, 1]. Usado para o modo paramétrico.

    Returns:
        float | list[float]
            - Se 'x' é fornecido, retorna o valor interpolado de 'y(x)' (float);
            - Se 't' é fornecido, retorna o vetor interpolado 'p(t)' (list[float]).

    Raises:
        ValueError
            - Se 'a' e 'b' têm dimensões diferentes;
            - Se nenhum ou ambos os parâmetros ('x', 't') são fornecidos;
            - Se 'x' é usado fora do intervalo definido por 'a' e 'b';
            - Se 'x' é usado com vetores que não pertencem a R²;
            - Se 't' não está no intervalo [0, 1].
    """
    vetor = []
    if len(a) != len(b):
        raise ValueError(f"Os pontos devem ser de mesma dimensão")
    
    if x is None and t is None:
        raise ValueError('Algum dos parâmetros deve ser passado (x ou t).')
    
    if x is not None and t is not None:
        raise ValueError('Apenas um dos parâmetros deve ser passado (x ou t).')
    
    if x is not None:
        if a[0] == a[1]:
            raise ValueError(f'Pontos consecutivos com mesmo x = {a[0]} geram um segmento vertical: interpolação indefinida.')
        if len(a) != 2 or len(b) != 2:
            raise ValueError('Interpolação por x só é válida para vetores no R2')
        x_min, x_max = sorted([a[0], b[0]])
        if not x_min <= x <= x_max:
            raise ValueError(f"x={x} está fora do intervalo [{x_min}, {x_max}].")
        return a[1] + (b[1] - a[1])/(b[0] - a[0]) * (x - a[0])
        
    if t is not None: 
        if not 0 <= t <= 1:
            raise ValueError('t deve estar entre 0 e 1.')
        for coords1, coords2 in zip(a, b): 
            vetor.append((1-t) * coords1 + t * coords2)
        return vetor
