"""
Testes unitários para a classe InterpoladorPolinomial.

Este script usa pytest para verificar o comportamento da classe,
incluindo o tratamento de erros na inicialização e a
corretude dos valores de interpolação.
"""

import pytest

from cb2325numericag8.interpolacao.interpolador_polinomial import InterpoladorPolinomial


def test_listas_tamanhos_diferentes():
    """
    Testa se a classe levanta um ValueError se as listas
    tiverem tamanhos diferentes.
    """
    with pytest.raises(ValueError, match="tamanhos diferentes"):
        InterpoladorPolinomial(
            valores_x=[0, 1],
            valores_y=[1]  # Lista com tamanho 1
        )

    with pytest.raises(ValueError, match="tamanhos diferentes"):
        InterpoladorPolinomial(
            valores_x=[0],  # Lista com tamanho 1
            valores_y=[1, 2]
        )


def test_listas_vazias():
    """
    Testa se a classe levanta um ValueError se as listas estiverem vazias.
    """
    with pytest.raises(ValueError, match="não podem estar vazias"):
        InterpoladorPolinomial([], [])


def test_valores_duplicados():
    """
    Testa se a classe levanta um ValueError se valores duplicados
    ocorrerem na lista x.
    """
    with pytest.raises(ValueError, match="números repetidos"):
        InterpoladorPolinomial(
            valores_x=[1, 2, 1],  # '1' está duplicado
            valores_y=[1, 2, 3]
        )


def test_tipo_entrada_invalido():
    """
    Testa se a classe levanta um TypeError se as entradas
    não forem listas.
    """
    with pytest.raises(TypeError, match="duas listas como entrada"):
        InterpoladorPolinomial(
            valores_x="não é uma lista",
            valores_y=[1, 2]
        )

    with pytest.raises(TypeError, match="duas listas como entrada"):
        InterpoladorPolinomial(
            valores_x=[1, 2],
            valores_y=None
        )


def test_polinomio_cubico_simples():
    """
    Testa a corretude da interpolação com os dados do
    bloco __main__ original.
    Polinômio: P(x) = 1.5x^3 - 6x^2 + 5.5x + 1
    """
    valores_x_teste = [0, 1, 2, 3]
    valores_y_teste = [1, 2, 0, 4]

    p = InterpoladorPolinomial(valores_x_teste, valores_y_teste)

    # 1. Verifica os pontos de interpolação (devem ser exatos)
    assert p(0.0) == pytest.approx(1.0)
    assert p(1.0) == pytest.approx(2.0)
    assert p(2.0) == pytest.approx(0.0)
    assert p(3.0) == pytest.approx(4.0)

    # 2. Verifica pontos intermediários (calculados manualmente)
    assert p(1.5) == pytest.approx(0.8125)
    assert p(0.5) == pytest.approx(2.4375)

    # 3. Verifica extrapolação (fora do intervalo [0, 3])
    assert p(4.0) == pytest.approx(23.0)
    assert p(-1.0) == pytest.approx(-12.0)


def test_caching_coeficientes_iterativo():
    """
    Testa se o mecanismo de cache dos coeficientes iterativos funciona.
    """
    valores_x_teste = [0, 1, 2, 3]
    valores_y_teste = [1, 2, 0, 4]

    p = InterpoladorPolinomial(valores_x_teste, valores_y_teste)

    # 1. Antes da chamada, o cache deve estar vazio (None)
    assert p._coef_iterativo_cache is None

    # 2. Faz a primeira chamada (isso deve preencher o cache)
    p(1.5)

    # 3. O cache não deve mais ser None
    assert p._coef_iterativo_cache is not None

    # 4. Verifica se o cache contém os coeficientes corretos
    # Coefs: [f[x0], f[x0,x1], f[x0,x1,x2], f[x0,x1,x2,x3]]
    coef_esperados = [1.0, 1.0, -1.5, 1.5]
    assert p._coef_iterativo_cache == pytest.approx(coef_esperados)

    # 5. Guarda o cache, modifica-o e verifica se a classe
    # usa o cache (mesmo que esteja "errado"), provando que o cache
    # está sendo usado e o cálculo não foi refeito.
    p._coef_iterativo_cache = [1, 1, 1, 1]  # Modifica o cache
    
    # P(1.5) com [1,1,1,1] = 1 + 1(1.5) + 1(1.5)(0.5) + 1(1.5)(0.5)(-0.5)
    # = 1 + 1.5 + 0.75 - 0.375 = 2.875
    assert p(1.5) == pytest.approx(2.875)
    assert p(1.5) != pytest.approx(0.8125)  # Não é o valor original
