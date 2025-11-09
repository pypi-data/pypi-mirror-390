import numpy as np
import matplotlib.pyplot as plt
class InterpolacaoLinearPorPartes:
    
    '''
    Cria um objeto para ser interpolado por partes.
    '''
    
    def __init__(self, lista_x:list, lista_y:list):

        '''
        Inicia o objeto.

        Args:
            lista_x (lista): lista com as coordenadas x dos pontos de base para a interpolação.
            lista_y (lista): lista com as coordenadas y dos pontos de base para a interpolação.
        
        Raises:
            ValueError: Se as listas não tem a mesma quantidade de elementos.
            ValueError: Se a lista de abscissas possui valores repetidos.
        '''

        if len(lista_x)!=len(lista_y):
            raise ValueError('As listas devem ter a mesma quantidade de elementos.')
        if len(lista_x)!=len(set(lista_x)):
            raise ValueError('A lista de abscissas possui valores repetidos.')

        self.x = np.array(lista_x)
        self.y = np.array(lista_y)

    def reta(self,i):        

        '''
        Retorna os coeficientes da reta que passa por dois pontos consecutivos do array de pontos self.x.

        Args:
            i (int): Índice do ponto extremo esquerdo da reta a ser calculada.

        Return:
            float: Coeficiente angular da reta.
            float: Coeficiente linear da reta.
        '''

        coef_angular = (self.y[i+1]-self.y[i])/(self.x[i+1]-self.x[i])
        coef_linear = self.y[i] - self.x[i]*coef_angular
      
        return coef_angular, coef_linear

    def __call__(self, x):

        '''
        Realiza a interpolação linear por partes em um ponto.

        Args:
            x (float): Coordenada x do ponto que se deseja interpolar.    
        
        Raises:
            ValueError: O valor de x está fora dos limites de self.x (extrapolação).

        Return:
            float: Coordenada y do ponto interpolado.
        '''

        if x<self.x[0] or x>self.x[-1]:
            raise ValueError('Erro de Extrapolação: a abscissa a ser avaliada está fora do intrevalo de interpolação.')
        elif x==self.x[-1]:
            return self.y[-1] 
        else:
            i = 0
            while True:
                if self.x[i]<=x<self.x[i+1]: 
                    break
                i+=1
                
            a,b = self.reta(i)
        
            return a*x+b
        
    def calcular_retas(self):      
  
        '''
        Cria um atributo do objeto: uma array com todas as retas entre cada par de pontos consecutivos de self.x.
       
        É Eficiente caso muitos pontos sejam interpolados (mais que len(self.x)).

        Return:
            array: Array com as tuplas que contém os coeficientes angulares e lineares da reta entre cada par de pontos consecutivos de self.x.
        '''

        lista = []
        
        for i in range(len(self.x)-1):
            a,b = self.reta(i) 
            lista.append((a,b))
      
        self.retas = np.array(lista)

        return self.retas

    def interpolar_muitos_pontos(self,x):
        
        '''
        Realiza a interpolação linear por partes em um ponto.

        Utiliza a lista de retas criada pela função 'calcular_retas'.

        A diferença desta função para '__call__' é que 'interpolar_muitos_pontos' é mais eficiente caso sejam realizadas muitas interpolações.

        Args:
            x (float): Coordenada x do ponto que se deseja interpolar.    
        
        Raises:
            ValueError: O valor de x está fora dos limites de self.x (extrapolação).

        Return:
            float: Coordenada y do ponto interpolado.
        '''

        if x<self.x[0] or x>self.x[-1]:
            raise ValueError('Erro de Extrapolação: a abscissa a ser avaliada está fora do intrevalo de interpolação.')
        elif x == self.x[-1]:
            return self.y[-1]
        else:    
            i = 0
            while True:
                if self.x[i]<=x<self.x[i+1]: 
                    break
                i+=1
        
        y = self.retas[i][0]*x+self.retas[i][1]

        return y

#TESTES:

if __name__ == '__main__':

    #1 - Teste do interpolador '__call__':

    x = [1,2,3,5]
    y = [2,4,8,32]
    interpolador_1 = InterpolacaoLinearPorPartes(x,y)

    print(interpolador_1(4)) #saída esperada: 20.0

    #2 - Teste de 'calcular_retas' e 'interpolar_muitos_pontos':

    a = [2,3,4]
    b = [4,9,16]
    interpolador_2 = InterpolacaoLinearPorPartes(a,b)

    interpolador_2.calcular_retas()

    pontos_interpolados = []
    for i in range(40):
        k=2+i/20
        pontos_interpolados.append((k,float(interpolador_2.interpolar_muitos_pontos(k))))

    print(pontos_interpolados) #saída esperada: lista com os pontos interpolados
