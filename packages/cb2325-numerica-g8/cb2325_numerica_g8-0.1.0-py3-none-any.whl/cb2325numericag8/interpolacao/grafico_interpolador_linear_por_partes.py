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

    # 🔹 Função gráfica integrada diretamente à classe
    def plotar(self, pontos_interpolados=None, titulo="Interpolação Linear por Partes"):
        """
        Exibe o gráfico da interpolação linear por partes com matplotlib.

        Args:
            pontos_interpolados (list[tuple], opcional): lista de (x, y) para destacar.
            titulo (str): título do gráfico.
        """
        plt.figure(figsize=(8, 5))
        plt.title(titulo)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True, linestyle="--", alpha=0.5)

        if not hasattr(self, "retas"):
            self.calcular_retas()

        # Desenha cada segmento linear
        for i in range(len(self.x) - 1):
            x_seg = np.linspace(self.x[i], self.x[i + 1], 100)
            a, b = self.retas[i]
            y_seg = a * x_seg + b
            plt.plot(x_seg, y_seg, color="blue", linewidth=1.8)

        # Pontos base
        plt.scatter(self.x, self.y, color="red", label="Pontos base", zorder=5)

        # Pontos interpolados (opcional)
        if pontos_interpolados:
            px, py = zip(*pontos_interpolados)
            plt.scatter(px, py, color="green", marker="x", s=70, label="Pontos interpolados", zorder=5)

        plt.legend()
        plt.tight_layout()
        plt.show()


# --------------------------
# 🔧 TESTE DIRETO
# --------------------------
if __name__ == "__main__":
    x = [1, 2, 3, 5]
    y = [2, 4, 8, 32]
    interp = InterpolacaoLinearPorPartes(x, y)
    interp.calcular_retas()

    # Gera pontos interpolados para o gráfico
    pontos = [(k, interp.interpolar_muitos_pontos(k)) for k in np.linspace(1, 5, 20)]

    # Agora basta chamar:
    interp.plotar(pontos)
