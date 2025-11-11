import numpy as np
import matplotlib.pyplot as plt
from cb2325numericag8.grafico.grafico_interpolacao_hermite import grafico_hermite

class InterpoladorHermite():
    """
    Calcula o polinômio interpolador de Hermite.

    Esta classe recebe listas de pontos x, valores y (f(x)) e
    valores da derivada y' (f'(x)) e calcula o polinômio
    interpolador que passa por esses pontos e tem essas derivadas.

    Atributos:
        valorx (list): A lista de coordenadas x dos pontos.
        valory (list): A lista de coordenadas y (valores de f(x)).
        valory_deriv (list): A lista de derivadas (valores de f'(x)).
        _coef (list): Cache para os coeficientes calculados.
        _z_nodes (list): Cache para os nós duplicados (z).
    """

    def __init__(self, valorx: list, valory: list, valory_deriv: list):
        """
        Inicializa o interpolador de Hermite.

        Args:
            valorx (list): Lista de valores x.
            valory (list): Lista de valores f(x).
            valory_deriv (list): Lista de valores da derivada f'(x).

        Raises:
            ValueError: Se as listas estiverem vazias ou tiverem tamanhos diferentes,
                        ou se a lista `valorx` contiver valores duplicados.
        """

        if (not isinstance(valorx, list) or
            not isinstance(valory, list) or
            not isinstance(valory_deriv, list)):
                raise TypeError("Não são listas")

        n = len(valorx)
        if not valorx:
                raise ValueError('As listas não podem estar vazias')

        if  n != len(valory) or n != len(valory_deriv):
            raise ValueError('As listas devem ter o mesmo tamanho')

        # Os valores devem ser distintos
        if len(set(valorx)) != n:
            raise ValueError(
                'Hermite requer valores de x de entrada distintos.'
            )

        # Converte tudo para float para segurança
        self.valorx = [float(v) for v in valorx]
        self.valory = [float(v) for v in valory]
        self.valory_deriv = [float(v) for v in valory_deriv]

        # Atributos para memoria dos coeficientes
        self._coef = None
        self._z_nodes = None

    def _calc_coefficients(self):
        """
        Calcula os coeficientes da tabela de diferenças divididas de Hermite como
        https://en.wikipedia.org/wiki/Divided_differences#Example.

        Args:
            None. Metódo que depende somente dos atributos da classe.

        Returns:
            None. Modifica apenas a memória interna da classe.
        """
        n = len(self.valorx)
        m = 2 * n

        z_nodes = [0.0] * m
        coef = [0.0] * m  # Armazena a diagonal da tabela de dif. divididas

        # z_nodes = [x0, x0, x1, x1, ...]
        # coef = [y0, y0, y1, y1, ...]
        for i in range(n):
            z_nodes[2 * i] = self.valorx[i]
            z_nodes[2 * i + 1] = self.valorx[i]
            coef[2 * i] = self.valory[i]
            coef[2 * i + 1] = self.valory[i]

        # Iteramos de trás para frente
        # coef[i] = f[z_{i-1}, z_i]
        # note que os denominadores nunca são zeros
        for i in range(m - 1, 0, -1):
            if i % 2 == 1:
                # Definimos a diferenças quando i par como sendo a derivada
                coef[i] = self.valory_deriv[i // 2]
            else:
                denominador = z_nodes[i] - z_nodes[i - 1]
                coef[i] = (coef[i] - coef[i - 1]) / denominador

        # Calcula as colunas restantes
        for j in range(2, m):
            for i in range(m - 1, j - 1, -1):
                # f[z_{i-j}, ..., z_i] = (f[z_{i-j+1}, ..., z_i] - f[z_{i-j}, ..., z_{i-1}]) / (z_i - z_{i-j})
                denominador = z_nodes[i] - z_nodes[i - j]
                coef[i] = (coef[i] - coef[i - 1]) / denominador

        self._coef = coef
        self._z_nodes = z_nodes

    def __call__(self, x: float) -> float:
        """
        Avalia o polinômio interpolador de Hermite em um ponto x.
        Usa a forma de Newton do polinômio:
        H(x) = c0 + c1(x-z0) + c2(x-z0)(x-z1) + ...

        Args:
            x (float): O ponto onde o polinômio será avaliado.

        Returns:
            float: O valor do polinômio H(x).
        """
        if self._coef is None:
            self._calc_coefficients()

        # Para fazer o typechecker não gritar comigo
        assert self._coef is not None, "Coeficientes não foram calculados."
        assert self._z_nodes is not None, "Os nós Z não foram calculados."

        m = len(self._coef)
        k = 0.0
        prod = 1.0

        for i in range(m):
            k += self._coef[i] * prod
            prod *= (x - self._z_nodes[i])

        return k

    def grafico(self):

        '''
        Plota os segmentos de retas do interpolador
        '''

        grafico_hermite(self)
        
