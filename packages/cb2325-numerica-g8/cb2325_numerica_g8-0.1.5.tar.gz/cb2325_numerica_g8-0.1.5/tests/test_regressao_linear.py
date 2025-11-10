import pytest
from cb2325numericag8.aproximacao.regressao_linear import ajuste_linear

def test_listas_tamanhos_diferentes():
    """
    Testa se a função levanta ValueError quando as listas têm tamanhos diferentes.
    """
    with pytest.raises(ValueError):
        ajuste_linear([1, 2, 3], [2, 3])

def test_tipos_invalidos():
    """
    Testa se a função levanta TypeError quando x ou y não são listas numéricas.
    """
    with pytest.raises(TypeError):
        ajuste_linear("abc", [1, 2, 3], plot=False)
    with pytest.raises(TypeError):
        ajuste_linear([1, 2, 3], None, plot=False)

def test_reta_perfeita():
    """
    Testa se a função retorna coeficientes corretos para y = 2x + 1.
    """
    x = [0, 1, 2, 3]
    y = [1, 3, 5, 7]
    a, b = ajuste_linear(x, y, plot=False)
    assert a == pytest.approx(2.0)
    assert b == pytest.approx(1.0)

def test_dados_com_ruido():
    """
    Testa se o ajuste linear funciona para dados com pequeno ruído.
    """
    import numpy as np
    np.random.seed(42)
    x = np.linspace(0, 10, 20)
    y = 3 * x + 2 + np.random.normal(0, 0.5, len(x))
    a, b = ajuste_linear(x, y, plot=False)
    assert a == pytest.approx(3, abs=0.3)
    assert b == pytest.approx(2, abs=0.5)

def test_resultado_numerico_simples():
    """
    Testa um caso numérico simples conhecido.
    """
    x = [1, 2, 3, 4]
    y = [2, 3, 5, 7]
    a, b = ajuste_linear(x, y, plot=False)
    assert a == pytest.approx(1.7, rel=1e-1)
    assert b == pytest.approx(0.0, rel=1e-1)
