import numpy as np
import matplotlib.pyplot as plt
from grafico.grafico_interpolacao_newton import plot

class InterpoladorPolinomial:
    """
    Cria um objeto de polinômio interpolador usando o método de Newton.

    Esta classe recebe listas de pontos (x, y) e pode calcular os
    coeficientes do polinômio de Newton. Ela armazena os coeficientes
    em cache após o primeiro cálculo para avaliações rápidas.

    Contém implementações para cálculo de coeficientes de forma
    iterativa (padrão) e recursiva (alternativa).

    Atributos:
        valores_x (list): A lista de coordenadas x dos pontos.
        valores_y (list): A lista de coordenadas y (valores de f(x)).
        _cache_coef_recursivo (dict): Cache para o método recursivo.
        _coef_iterativo_cache (list | None): Cache para os coeficientes do
                                             método iterativo.
    """

    def __init__(self, valores_x: list, valores_y: list):
        """
        Inicializa o interpolador de Newton.

        Args:
            valores_x (list): Lista de valores x.
            valores_y (list): Lista de valores f(x).

        Raises:
            TypeError: Se as entradas 'valores_x' ou 'valores_y' não forem
                       listas.
            ValueError: Se as listas estiverem vazias, tiverem tamanhos
                        diferentes, ou se a lista `valores_x` contiver
                        valores duplicados.
        """
        if not isinstance(valores_x, list) or not isinstance(valores_y, list):
            raise TypeError('A função recebe duas listas como entrada')

        n = len(valores_x)
        if not valores_x:
            raise ValueError('As listas não podem estar vazias')

        if n != len(valores_y):
            raise ValueError('As listas têm tamanhos diferentes')

        if len(set(valores_x)) != n:
            raise ValueError(
                'A entrada dos valores de x contém números repetidos'
            )

        self.valores_x = valores_x
        self.valores_y = valores_y

        # Cache para o método recursivo
        self._cache_coef_recursivo = {}

        # Cache para o método iterativo (usado por __call__)
        self._coef_iterativo_cache = None

    def _calcular_coef_recursivo(
        self, valores_x_sub: list, valores_y_sub: list, lista_saida: list
    ):
        """
        Calcula coeficientes recursivamente com memoização.

        Nota: Este método modifica 'lista_saida' por referência.

        Args:
            valores_x_sub (list): Sub-lista de valores x para esta recursão.
            valores_y_sub (list): Sub-lista de valores y para esta recursão.
            lista_saida (list): Lista de coeficientes sendo construída.

        Returns:
            list: Uma lista [coeficiente_final, lista_de_coeficientes]
        """
        if len(valores_x_sub) == 1:
            return [float(valores_y_sub[0]), lista_saida]
        else:
            if tuple(valores_x_sub[1:]) in self._cache_coef_recursivo:
                if tuple(valores_x_sub[:-1]) in self._cache_coef_recursivo:
                    a = self._cache_coef_recursivo[tuple(valores_x_sub[1:])]
                    b = self._cache_coef_recursivo[tuple(valores_x_sub[:-1])]
                else:
                    a = self._cache_coef_recursivo[tuple(valores_x_sub[1:])]
                    b_result = self._calcular_coef_recursivo(
                        valores_x_sub[:-1], valores_y_sub[:-1], lista_saida
                    )
                    b = b_result[0]
                    self._cache_coef_recursivo[tuple(valores_x_sub[:-1])] = b
            elif tuple(valores_x_sub[:-1]) in self._cache_coef_recursivo:
                if tuple(valores_x_sub[1:]) in self._cache_coef_recursivo:
                    a = self._cache_coef_recursivo[tuple(valores_x_sub[1:])]
                    b = self._cache_coef_recursivo[tuple(valores_x_sub[:-1])]
                else:
                    b = self._cache_coef_recursivo[tuple(valores_x_sub[:-1])]
                    a_result = self._calcular_coef_recursivo(
                        valores_x_sub[1:], valores_y_sub[1:], []
                    )
                    a = a_result[0]
                    self._cache_coef_recursivo[tuple(valores_x_sub[1:])] = a
            else:
                a_result = self._calcular_coef_recursivo(
                    valores_x_sub[1:], valores_y_sub[1:], []
                )
                a = a_result[0]
                b_result = self._calcular_coef_recursivo(
                    valores_x_sub[:-1], valores_y_sub[:-1], lista_saida
                )
                b = b_result[0]
                self._cache_coef_recursivo[tuple(valores_x_sub[1:])] = a
                self._cache_coef_recursivo[tuple(valores_x_sub[:-1])] = b

            denominador = float(valores_x_sub[-1]) - float(valores_x_sub[0])

            if len(valores_x_sub) > 2:
                lista_saida.append(b)

            if denominador == 0:
                raise ValueError(
                    'A entrada dos valores de x contém números repetidos'
                )

            return [(a - b) / denominador, lista_saida]

    def _calcular_coef_iterativo(self):
        """
        Calcula os coeficientes iterativamente (O(n^2)).
        O resultado é armazenado em 'self._coef_iterativo_cache'.

        Args:
            None.
        """
        n = len(self.valores_x)
        coef = np.array(self.valores_y, dtype=float)

        for j in range(1, n):
            for i in range(n - 1, j - 1, -1):
                denominador = (self.valores_x[i] - self.valores_x[i - j])

                if denominador == 0:
                    raise ValueError(
                        'A entrada dos valores de x contém números repetidos'
                    )

                coef[i] = (coef[i] - coef[i - 1]) / denominador

        self._coef_iterativo_cache = coef.tolist()  # Armazena no cache

    def __call__(self, x: float) -> float:
        """
        Avalia o polinômio interpolador em um ponto 'x'.
        Calcula os coeficientes (iterativamente) apenas na primeira chamada.

        Args:
            x (float): O ponto onde o polinômio será avaliado.

        Returns:
            float: O valor do polinômio P(x).
        """

        # --- Abordagem 1: Iterativa (com cache) ---

        # Calcula os coeficientes APENAS se o cache estiver vazio
        if self._coef_iterativo_cache is None:
            self._calcular_coef_iterativo()

        # Garante ao Python que o cache não é None
        assert self._coef_iterativo_cache is not None, "Cache não preenchido."
        coef = self._coef_iterativo_cache

        # --- Abordagem 2: Recursiva (Alternativa) ---
        # Para usar o método recursivo, descomente as linhas abaixo.

        # self._cache_coef_recursivo = {}  # Limpa o cache
        # lista = self._calcular_coef_recursivo(
        #     self.valores_x, self.valores_y, [self.valores_y[0]]
        # )
        # coef = lista[1] + [lista[0]]

        # --- Avaliação do Polinômio ---
        k = 0
        prod = 1
        for i in range(len(self.valores_x)):
            k += coef[i] * prod
            prod *= (x - self.valores_x[i])

        return k
        

if __name__ == "__main__":
    """
    Bloco de teste para executar o código.
    """
    print("Executando teste do InterpoladorNewton...")

    # Pontos de entrada
    valores_x_teste = [0, 1, 2, 3]
    valores_y_teste = [1, 2, 0, 4]

    num_pontos_plot = 500

    try:
        p = InterpoladorPolinomial(valores_x_teste, valores_y_teste)

        ponto_teste_1 = 1.5
        # Primeira chamada: calcula e armazena os coeficientes
        resultado_1 = p(ponto_teste_1)
        print(f"P({ponto_teste_1}) = {resultado_1:.4f}")

        # Segunda chamada: usa os coeficientes do cache (rápido)
        ponto_teste_2 = 0.5
        resultado_2 = p(ponto_teste_2)
        print(f"P({ponto_teste_2}) = {resultado_2:.4f}")

        print("Gerando gráfico...")
        p.plot(num_pontos_plot)

    except (ValueError, TypeError) as e:
        print(f"Erro ao criar ou avaliar o interpolador: {e}")
        
