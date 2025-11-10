import pytest
import numpy as np
from cb2325numericag8.integracao.integracao import integral, integral_trapezoidal, integral_simpson


funcao1 = lambda x: np.sin(x)
funcao2 = lambda x: 1 / x
funcao3 = lambda x: x**2
funcao4 = lambda x: np.exp(x)
funcao5 = lambda x: np.sqrt(x) 


def test_funcao1():
    """
    Testa se a integral de sin(x) em [0, pi] resulta em aproximadamente 2 utilizando ambos os métodos.
    """

    resultado1 = integral_trapezoidal(funcao1, 0, np.pi, n=100)
    assert np.isclose(resultado1, 2.0, rtol=1e-3)

    resultado2 = integral_simpson(funcao1, 0, np.pi, n=50)
    assert np.isclose(resultado2, 2.0, rtol=1e-6)


def test_funcao2():
    """
    Testa se a integral de 1/x em [1, 2] resulta em aproximadamente ln(2) utilizando ambos os métodos.
    """

    resultado1 = integral_trapezoidal(funcao2, 1, 2, n=50)
    assert np.isclose(resultado1, np.log(2), rtol=1e-3)

    resultado2 = integral_simpson(funcao2, 1, 2, n=50)
    assert np.isclose(resultado2, np.log(2), rtol=1e-6)


def test_funcao3():
    """
    Testa se a integral de x^2 em [0, 1] resulta em aproximadamente 1/3 utilizando ambos os métodos.
    """

    resultado1 = integral_trapezoidal(funcao3, 0, 1, n=50)
    assert np.isclose(resultado1, 1 / 3, rtol=1e-3)

    resultado2 = integral_simpson(funcao3, 0, 1, n=10)
    assert np.isclose(resultado2, 1 / 3, rtol=1e-6)


def test_funcao4():
    """
    Testa se a integral de exp(x) em [0, 1] resulta em aproximadamente e-1 utilizando ambos os métodos.
    """

    resultado1 = integral_trapezoidal(funcao4, 0, 1, n=50)
    assert np.isclose(resultado1, np.exp(1) - 1, rtol=1e-3)

    resultado2 = integral_simpson(funcao4, 0, 1, n=50)
    assert np.isclose(resultado2, np.exp(1) - 1, rtol=1e-6)


def test_funcao5():
    """
    Testa se a integral de sqrt(x) em [0, 1] resulta em aproximadamente 2/3 utilizando ambos os métodos.
    """

    resultado1 = integral_trapezoidal(funcao5, 0, 1, n=100)
    assert np.isclose(resultado1, 2 / 3, rtol=1e-3)

    resultado2 = integral_simpson(funcao5, 0, 1, n=100)
    assert np.isclose(resultado2, 2 / 3, rtol=1e-3)


def test_trapezoidal_precisao():
    """
    Testa se o resultado é arredondado corretamente quando a precisão é fornecida.
    """

    resultado = integral_trapezoidal(funcao3, 0, 1, n=50, precisao=3)
    assert isinstance(resultado, float)
    assert len(str(resultado).split(".")[-1]) <= 3


def test_limites_invertidos():
    """
    Testa se o valor da integral troca quando os limites são invertidos.
    """

    resultado1 = integral_trapezoidal(funcao3, 0, 1, n=100)
    resultado2 = integral_trapezoidal(funcao3, 1, 0, n=100)
    assert np.isclose(resultado2, -resultado1, rtol=1e-10)


def test_metodo_invalido():
    """
    Testa se retorna erro ao tentar utilizar um método inválido.
    """

    with pytest.raises(ValueError, match="método escolhido é inválido"):
        integral(funcao1, 0, np.pi, metodo="invalido")

    with pytest.raises(ValueError, match="o método informado deve ser uma string"):
        integral(funcao1, 0, np.pi, metodo=123)


def test_integral_chama():
    """
    Testa se integral() chama os métodos corretamente.
    """

    resultado1 = integral(funcao3, 0, 1, metodo="Simpson")
    assert np.isclose(resultado1, 1 / 3, rtol=1e-6)

    resultado2 = integral(funcao3, 0, 1, metodo="Trapezoidal")
    assert np.isclose(resultado2, 1 / 3, rtol=1e-3)


def test_intervalo_invalido():
    """
    Testa se ocorre erro ao tentar avaliar uma função não definida em um ponto.
    """

    with pytest.warns(RuntimeWarning, match="divide by zero"):
        with pytest.raises(ValueError, match="não definida"):
            integral(funcao2, -1, 1, metodo="Trapezoidal")

    with pytest.warns(RuntimeWarning, match="divide by zero"):
        with pytest.raises(ValueError, match="não definida"):
            integral(funcao2, -1, 1, metodo="Simpson")


def test_simpson_corrige_n_impar(capsys):
    """
    Testa se o método de Simpson força um número ímpar de subdivisões.
    """

    resultado = integral_simpson(funcao1, 0, np.pi, n=19)
    saida = capsys.readouterr().out
    assert "Ajustado para 20" in saida
    assert np.isclose(resultado, 2.0, rtol=1e-4)


def test_precisao_valores_invalidos():
    """
    Testa o comportamento do parâmetro 'precisao' em integral_trapezoidal e integral_simpson.
    As funções devem aceitar somente 0 ou inteiros positivos, além do valor padrão None.
    """

    precisao_validos = [0, 1, 5]
    precisao_invalidos = ["a", 3.5, [2], {"xy":np.pi}]
    
    for p in precisao_validos:
        res_trap = integral_trapezoidal(funcao3, 0, 1, n=50, precisao=p)
        res_simp = integral_simpson(funcao3, 0, 1, n=50, precisao=p)
        assert isinstance(res_trap, float)
        assert isinstance(res_simp, float)

        parte_dec_trap = str(res_trap).split(".")[-1]
        if p == 0:
            assert parte_dec_trap == "0"
        else:
            assert len(parte_dec_trap) <= p

        parte_dec_simp = str(res_simp).split(".")[-1]
        if p == 0:
            assert parte_dec_simp == "0"
        else:
            assert len(parte_dec_simp) <= p
    
    for p in precisao_invalidos:
        with pytest.raises(
            ValueError, match="precisão deve ser um inteiro não negativo"
        ):
            integral_trapezoidal(funcao3, 0, 1, n=50, precisao=p)
        with pytest.raises(
            ValueError, match="precisão deve ser um inteiro não negativo"
        ):
            integral_simpson(funcao3, 0, 1, n=50, precisao=p)
    
    with pytest.raises(
        ValueError, match="precisão deve ser um inteiro não negativo"
    ):
        integral_trapezoidal(funcao3, 0, 1, n=50, precisao=-1)
    with pytest.raises(
        ValueError, match="precisão deve ser um inteiro não negativo"
    ):
        integral_simpson(funcao3, 0, 1, n=50, precisao=-5)