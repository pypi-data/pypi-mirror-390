import pytest
import numpy as np

from cb2325numericag8.interpolacao.interpolador_linear_por_partes import InterpolacaoLinearPorPartes

#Dados para o Teste 1: 
X_1 = [1,2,3,4,5]
Y_1 = [1,2,3,4]

#Dados para o Teste 2:
X_2 = [1,2,3,3,4]
Y_2 = [1,2,3,4,5]

#Dados para os Testes 3,4,5,6,7:
X_3 = [1,2,3,5]
Y_3 = [2,4,8,32] 

#Teste 1 - Erro de inicialização de objeto com listas x,y de diferentes tamanhos:

def test_listas_de_tamanhos_diferentes():

    with pytest.raises(ValueError, match='As listas devem ter a mesma quantidade de elementos.'):
        objeto1 = InterpolacaoLinearPorPartes(X_1,Y_1)

#Teste 2 - Erro de inicialização do objeto com a lista x com valores repetidos:

def test_abscissas_repetidas():

    with pytest.raises(ValueError, match='A lista de abscissas possui valores repetidos.'):
        objeto2 = InterpolacaoLinearPorPartes(X_2,Y_2)

#Teste 3 - Função '__call__':

objeto3 = InterpolacaoLinearPorPartes(X_3,Y_3)
assert objeto3(4) == pytest.approx(20.0)

#Teste 4 - Função 'calcular_retas':

retas_esperadas = [(2,0),(4,-4),(12,-28)]
np.testing.assert_allclose(objeto3.calcular_retas(), retas_esperadas, rtol=1e-5, atol=0)
 
#Teste 5 - Função 'interpolar_muitos_pontos':

inter = [2, 2.5, 3, 3.5]
gremio = [4, 6, 8, 14]
for i in range(4):
    assert objeto3.interpolar_muitos_pontos(inter[i]) == pytest.approx(gremio[i])

#Teste 6 - Erro de extrapolação em '__call__' e 'interpolar_muitos_pontos':

def test_extrapolacao1():

    with pytest.raises(ValueError, match = 'Erro de Extrapolação'):
        objeto3(6)

def test_extrapolacao2():

    with pytest.raises(ValueError, match = 'Erro de Extrapolação'):
        objeto3.interpolar_muitos_pontos(6)

#Teste 7 - Função 'retas':

a,b = objeto3.reta(0)
t = (a,b)
assert t == pytest.approx((2,0))
