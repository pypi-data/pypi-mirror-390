import pytest
from cb2325numericag8.erros.erros import erro_absoluto 
from cb2325numericag8.erros.erros import erro_relativo
from cb2325numericag8.erros.erros import erro_quadratico_medio


def test_erro_absoluto_nao_numerico():
    """
    Verifica se a função 'erro_absoluto' levanta um ValueError
    quando um dos valores de entrada não é numérico.
    """
    mensagem_erro = "Erro: os valores real e aproximado devem ser numéricos."
    
    with pytest.raises(ValueError, match=mensagem_erro):
        erro_absoluto("string",3)

def test_erro_relativo_valor_real_zero():
    """
    Verifica se a função 'erro_relativo' levanta ValueError
    quando o valor real é zero.
    """
    mensagem_erro = "Erro: o valor real não pode ser zero para o cálculo do erro relativo."

    with pytest.raises(ValueError, match=mensagem_erro):
        erro_relativo(0,3)

def test_erro_relativo_não_numerico():
    """
    Verifica se a função 'erro_relativo' levanta um ValueError
    quando um dos valores de entrada não é numérico.
    """
    mensagem_erro = "Erro: os valores real e aproximado devem ser numéricos."

    with pytest.raises(ValueError, match=mensagem_erro):
        erro_relativo("string",3)

def test_erro_quadratico_medio_tamanhos_diferentes():
    """
    Verifica se a função 'erro_quadratico_medio' falha quando as listas de
    entrada tem tamanhos diferentes.
    """
    mensagem_erro = "Erro: as listas devem possuir a mesma quantidade de elementos."

    with pytest.raises(ValueError,match=mensagem_erro):
        lista_real = [1,2,3]
        lista_aproximada = [1,2]
        erro_quadratico_medio(lista_real, lista_aproximada)

def test_erro_quadratico_medio_listas_vazias():
    """
    Verifica se a função 'erro quadratico medio' falha quando
    as listas de entrada estão vazias.
    """
    mensagem_erro = "Erro: as listas não podem ser vazias."

    with pytest.raises(ValueError,match=mensagem_erro):
        erro_quadratico_medio([],[])

def test_erro_quadratico_medio_nao_numerico():
    """
    Verifica se a função 'erro_quadratico_medio' falha quando 
    um item das listas não é numérico.
    """
    mensagem_erro = "Erro: todos os valores das listas devem ser numéricos."

    with pytest.raises(ValueError,match=mensagem_erro):
        lista_real = [1,2]
        lista_aproximada = [1,"x"]
        erro_quadratico_medio(lista_real, lista_aproximada)

def test_precisao_valores_invalidos():
    """
    Testa o comportamento do parâmetro 'precisao' nas funções de cálculo de erros.
    As funções devem aceitar somente 0 ou inteiros positivos, além do valor padrão None.
    """

    precisao_validos = [0, 1, 5]
    precisao_invalidos = ["a", 3.5, [2], {"xy":1549}]
    
    for p in precisao_validos:
        ea = erro_absoluto(3, 4, precisao=p)
        er = erro_relativo(3, 4, precisao=p)
        eqm = erro_quadratico_medio([3, 3.5], [4, 3.4], precisao=p)
        assert isinstance(ea, float)
        assert isinstance(er, float)
        assert isinstance(eqm, float)

        parte_dec_ea = str(ea).split(".")[-1]
        if p == 0:
            assert parte_dec_ea == "0"
        else:
            assert len(parte_dec_ea) <= p

        parte_dec_er = str(er).split(".")[-1]
        if p == 0:
            assert parte_dec_er == "0"
        else:
            assert len(parte_dec_er) <= p
        
        parte_dec_eqm = str(eqm).split(".")[-1]
        if p == 0:
            assert parte_dec_eqm == "0"
        else:
            assert len(parte_dec_eqm) <= p
    
    for p in precisao_invalidos:
        with pytest.raises(
            ValueError, match="precisão deve ser um inteiro não negativo"
        ):
            erro_absoluto(3, 4, precisao=p)
        with pytest.raises(
            ValueError, match="precisão deve ser um inteiro não negativo"
        ):
            erro_relativo(3, 4, precisao=p)
        with pytest.raises(
            ValueError, match="precisão deve ser um inteiro não negativo"
        ):
            erro_quadratico_medio([3, 3.5], [4, 3.4], precisao=p)
    
    with pytest.raises(
        ValueError, match="precisão deve ser um inteiro não negativo"
    ):
        erro_absoluto(3, 4, precisao=-1)
    with pytest.raises(
        ValueError, match="precisão deve ser um inteiro não negativo"
    ):
        
        erro_relativo(3, 4, precisao=-5)
    with pytest.raises(
        ValueError, match="precisão deve ser um inteiro não negativo"
    ):
        erro_quadratico_medio([3, 3.5], [4, 3.4], precisao=-7)