# Teste da função erro relativo 
from src.erros import erro_relativo

def test_erro_relativo():
    assert erro_relativo(3.141592, 3.14) == 0.0005067
    assert erro_relativo(2.718282, 2.72) == 0.000632
    assert erro_relativo(1.414214, 1.41 ) == 0.0029797