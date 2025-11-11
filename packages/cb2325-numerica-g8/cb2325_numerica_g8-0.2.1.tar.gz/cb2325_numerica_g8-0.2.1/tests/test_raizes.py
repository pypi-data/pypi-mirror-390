#Testes do Módulo Raizes

import pytest
import math
import numpy as np
from cb2325numericag8.raizes.raizes import raiz 

# Exemplos de funções
def funcao1(x):
    return 2*x - x**2

def funcao2(x):
    return math.exp(x) - 2

def funcao3(x):
    return x**10 - 5

def derivada_funcao3(x):
    return 10 * x**9


def test_metodo_invalido():
    """
    Testa se a função levanta ValueError para método inválido.
    """
    with pytest.raises(ValueError, match="Método não reconhecido"):
        raiz(funcao1, a=0, b=3, method="nao_existe")

def test_bissecao_intervalo_invalido():
    """
    Testa se o método levanta ValueError quando o intervalo não contém raiz.
    """
    with pytest.raises(ValueError, match="mesmo sinal"):
        raiz(funcao1, a=3, b=4, tol=1e-6, method="bissecao")

def test_secante_divisao_por_zero():
    """
    Testa erro de divisão por zero no método da secante.
    """
    with pytest.raises(ZeroDivisionError, match="Divisão por zero"):
        raiz(funcao1, a=0, b=2, tol=1e-6, method="secante")

def test_newton_divisao_por_zero():
    """
    Testa erro de divisão por zero no método de Newton-Raphson.
    """
    with pytest.raises(ZeroDivisionError, match="Divisão por zero"):
        raiz(funcao3, a=0, f_prime=derivada_funcao3, tol=1e-6, method="newton_raphson")

def test_metodo_default_secante():
    """
    Testa o método padrão (secante) quando não é especificado.
    """
    r, _ = raiz(funcao1, 1, 3, tol=1e-6)
    assert pytest.approx(r, rel=1e-5) == 2

def test_bissecao():
    """
    Testa o método da bisseção.
    """
    r, _ = raiz(funcao3, 0, 4, tol=1e-6, method="bissecao")
    assert pytest.approx(r, rel=1e-5) == 5**0.1

def test_secante():
    """
    Testa o método da secante.
    """
    r, _ = raiz(funcao2, a=0, b=2, tol=1e-6, method="secante")
    assert pytest.approx(r, rel=1e-3) == 0.6931

def test_newton_com_derivada():
    """
    Testa Newton-Raphson com derivada explícita.
    """
    r, _ = raiz(funcao3, 2, tol=1e-6, f_prime=derivada_funcao3, method="newton_raphson")
    assert pytest.approx(r, rel=1e-5) == 5**0.1

def test_newton_sem_derivada():
    """
    Testa Newton-Raphson estimando derivada numericamente.
    """
    r, _ = raiz(funcao3, 2, tol=1e-6, method="newton_raphson")
    assert pytest.approx(r, rel=1e-5) == 5**0.1

def test_sem_convergencia():
    """
    Testa se a secante levanta RuntimeError quando não converge.
    """
    with pytest.raises(RuntimeError):
        raiz(funcao1, a=1, b=4, tol=1e-6, max_iter=5, method="secante")

def test_iteracoes_retorno_lista():
    """
    Verifica se todos os métodos retornam lista de iterações.
    """
    _, it1 = raiz(funcao1, 0, 2, method="bissecao")
    _, it2 = raiz(funcao2, 0, 2, method="secante")
    _, it3 = raiz(funcao3, 2, f_prime=derivada_funcao3, method="newton_raphson")
    assert isinstance(it1, list)
    assert isinstance(it2, list)
    assert isinstance(it3, list)
