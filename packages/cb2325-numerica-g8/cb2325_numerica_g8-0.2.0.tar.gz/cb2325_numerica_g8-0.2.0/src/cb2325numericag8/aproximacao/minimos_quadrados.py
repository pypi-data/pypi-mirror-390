import numpy as np
from cb2325numericag8.grafico.grafico_minimos_quadrados import plot_aproximacao
from cb2325numericag8.aproximacao.regressao_linear import ajuste_linear

def AproximacaoPolinomial(abscissas: list, ordenadas: list, grau: int = 1, plot: bool = False, n: int = 500) -> list:
    """
    Aproxima os pontos (x, y) por um polinômio de grau n usando mínimos quadrados e plota o gráfico.

    Parâmetros:
        abscissas (list ou tuple): coordenadas x
        ordenadas (list ou tuple): coordenadas y
        grau (int, opicional): grau do polinômio. Padrão é 1
        plot (bool, opicional): Se True, plota o gráfico. Padrão é False
        n (int, opcional): Número de pontos para a curva suave caso plot = True . Padrão é 500
    
    Raises:
        TypeError: Se as abscissas não forem do tipo 'list' ou 'tuple'
        TypeError: Se as ordenadas não forem do tipo 'list' ou 'tuple'
        TypeError: Se o grau fornecido não for um 'int' ou um 'float' com parte decimal igual a 0
        ValueError: Se as abscissas ou as ordenadas form listas vazias
        ValueError: Se o grau fornecido for menor que 1
        ValueError: Se as abicissas e as ordenadas tiverem um número diferente de elementos
        ValueError: Se o grau fornecido for maior ou igual à quantidade de abcissas e ordenadas
        
    Retorna:
        list: coeficientes do polinômio aproximado, do maior para o menor grau
    """
    
    if not isinstance(abscissas, (list, tuple)):
        raise TypeError(
            "O argumento 1 de AproximacaoPolinomial (abscissas) precisa ser 'list' ou 'tuple'"
        )
    
    if not isinstance(ordenadas, (list, tuple)):
        raise TypeError(
            "O argumento 2 de AproximacaoPolinomial (ordenadas) precisa ser 'list' ou 'tuple'"
        )
            
    if not isinstance(grau, int):
        if isinstance(grau, float):
            if grau != int(grau):
                raise TypeError(
                    "O argumento 3 de AproximacaoPolinomial (grau do polinômio) precisa ser 'int'"
            )
        raise TypeError(
            "O argumento 3 de AproximacaoPolinomial (grau do polinômio) precisa ser 'int'"
        )
    
    if len(abscissas) == 0:
        raise ValueError(
            "A quantidade de abscissas (argumento 1) precisa ser maior que 0"
        )
    
    if len(ordenadas) == 0:
        raise ValueError(
            "A quantidade de ordenadas (argumento 2) precisa ser maior que 0"
        )
    
    if grau<1:
        raise ValueError(
            "O grau do polinômio aproximado (argumento 3) precisa ser maior ou igual a 1"
        )
    
    if len(abscissas) != len(ordenadas):
        if len(abscissas) < len(ordenadas):
            raise ValueError(
                "O número de abscissas (argumento 1) é menor que o número de ordenadas (argumento 2)"
            )
        raise ValueError(
            "O número de abscissas (argumento 1) é maior que o número de ordenadas (argumento 2)"
        )

    if len(abscissas) <= grau:
        raise ValueError(
            "O grau do polinômio aproximado (argumento 3) deve ser menor que o número de pontos fornecidos (argumento 1)"
        )
    
    if grau == 1:
        return ajuste_linear(abscissas, ordenadas, plot)
    
    X = []
    for xi in abscissas:
        linha = []
        for j in range(grau, -1, -1):
            linha.append(xi**j)
        X.append(linha)

    X_array = np.array(X)
    y_array = np.array(ordenadas)
    beta = np.linalg.solve(X_array.T @ X_array, X_array.T @ y_array)
    
    # Transforma beta em uma lista padrão do python e arredonda para 10 casas decimais
    coeficientes = [float(f"{coef:.10f}") for coef in beta]
    
    if plot:
        plot_aproximacao(abscissas, ordenadas, coeficientes, n)
    
    return coeficientes

