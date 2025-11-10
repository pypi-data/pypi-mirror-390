import pytest

from cb2325numericag8.interpolacao.interpolador_hermite import InterpoladorHermite

def test_listas_tamanhos_diferentes():
    """
    Testa se a classe levanta um ValueError se as listas
    tiverem tamanhos diferentes.
    """
    with pytest.raises(ValueError, match="mesmo tamanho"):
        InterpoladorHermite(
            valorx=[0, 1],
            valory=[1, 2],
            valory_deriv=[1] # Lista com tamanho 1
        )

    with pytest.raises(ValueError, match="mesmo tamanho"):
        InterpoladorHermite(
            valorx=[0, 1],
            valory=[1], # Lista com tamanho 1
            valory_deriv=[1, 0]
        )

def test_listas_vazias():
    """
    Testa se a classe levanta um ValueError se as listas estiverem vazias.
    """
    with pytest.raises(ValueError, match="não podem estar vazias"):
        InterpoladorHermite([], [], [])

def test_valores_duplicados():
    """
    Testa se valores duplicados ocorrem na lista x.
    """
    with pytest.raises(ValueError, match="distintos."):
        InterpoladorHermite(
                valorx=[1, 1],
                valory=[1, 2],
                valory_deriv=[2, 3]
        )

def test_tipo_entrada_invalido():
    """
    Testa se a classe levanta um TypeError se as entradas
    não forem listas.
    """
    with pytest.raises(TypeError, match="são listas"):
        InterpoladorHermite(
            valorx="nope",
            valory=[1],
            valory_deriv=[1]
        )

    with pytest.raises(TypeError, match="são listas"):
        InterpoladorHermite(
            valorx=[1],
            valory=None,
            valory_deriv=[1]
        )

def test_polinomio_cubico_simples():
    """
    Testa se bate com os resultados esperados com um polinomio 
    H(x) = -x^3 + x^2 + x + 1
    """
    vetorx = [0, 1]
    vetory = [1, 2]
    vetory_deriv = [1, 0]

    p = InterpoladorHermite(vetorx, vetory, vetory_deriv)

    # Verifica os pontos de interpolação
    assert p(0.0) == pytest.approx(1.0)
    assert p(1.0) == pytest.approx(2.0)

    # Verifica pontos intermediários e externos
    assert p(0.5) == pytest.approx(1.625)
    assert p(2.0) == pytest.approx(-1.0)
    assert p(-1.0) == pytest.approx(2.0)
