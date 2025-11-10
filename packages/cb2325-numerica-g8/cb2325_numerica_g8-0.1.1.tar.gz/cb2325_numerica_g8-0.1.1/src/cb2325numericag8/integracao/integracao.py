import numpy as np
from cb2325numericag8.utils.kahan import soma_kahan
from cb2325numericag8.grafico.grafico_integracao import grafico_trapezoidal, grafico_simpson


def integral_trapezoidal(funcao, a, b, n=100, mostrar_grafico=False, precisao=None):
    """
    Integra numericamente uma função dada, utilizando uma aproximação trapezoidal.

    Args:
        funcao (callable): Expressão dada para a função.
        a (float): Limite inferior da integral.
        b (float): Limite superior da integral.
        n (int): Número de divisões do intervalo de integração. Valor padrão é 100.
        mostrar_grafico (bool, optional): Define se deve gerar o gráfico ou não. Valor padrão é False.
        precisao (int, optional): Número de casas decimais no resultado retornado.

    Raises:
        ValueError: Caso a função não possa ser avaliada em algum ponto.

    Returns:
        float: Valor numérico obtido para a integral arredondado 
        de acordo com a precisão, caso fornecida.
    """

    vals_x = np.linspace(a, b, n + 1)
    try:
        y = [funcao(x) for x in vals_x]
    except Exception as e:
        raise ValueError(f"Erro ao avaliar a função em algum ponto do intervalo: {e}")
    delta = (b - a) / n
    soma_intermediaria = soma_kahan(y[1:-1])
    valor_integral = (delta / 2) * soma_kahan([y[0], 2 * soma_intermediaria, y[-1]])

    if mostrar_grafico:
        grafico_trapezoidal(funcao, a, b, s=300, area=valor_integral, n=n)

    if precisao is not None:
        return round(valor_integral, precisao)
    return valor_integral


def integral_simpson(funcao, a, b, n=100, mostrar_grafico=False, precisao=None):
    """
    Integra numericamente uma função dada, utilizando o método de Simpson.

    Args:
        funcao (callable): Expressão dada para a função.
        a (float): Limite inferior da integral.
        b (float): Limite superior da integral.
        n (int): Número de divisões do intervalo de integração. Valor padrão é 100.
        mostrar_grafico (bool, optional): Define se deve gerar o gráfico ou não. Valor padrão é False.
        precisao (int, optional): Número de casas decimais no resultado retornado.
    
    Raises:
        ValueError: Caso a função não possa ser avaliada em algum ponto.

    Returns:
        float: Valor numérico obtido para a integral arredondado 
        de acordo com a precisão, caso fornecida.
    """

    if n % 2 != 0:
        n += 1
        print(f"Aviso: número de divisões do intervalo de integração deve ser par. Ajustado para {n}.")

    vals_x = np.linspace(a, b, n + 1)
    try:
        y = [funcao(x) for x in vals_x]
    except Exception as e:
        raise ValueError(f"Erro ao avaliar a função em algum ponto do intervalo: {e}")
    delta = (b - a) / n

    soma_imp = soma_kahan(y[1:-1:2])
    soma_par = soma_kahan(y[2:-2:2])

    valor_integral = (delta / 3) * soma_kahan([y[0], 4 * soma_imp, 2 * soma_par, y[-1]])

    if mostrar_grafico:
        grafico_simpson(funcao, a, b, s=300, area=valor_integral, n=n)

    if precisao is not None:
        return round(valor_integral, precisao)
    return valor_integral


metodos_integral = {
    'Trapezoidal': integral_trapezoidal,
    'Simpson': integral_simpson,
}


def integral(funcao, a, b, n=100, mostrar_grafico=False, precisao=None, metodo='Trapezoidal'):
    """
    Integra numericamente uma função dada, utilizando o método escolhido.

    Args:
        funcao (callable): Expressão dada para a função.
        a (float): Limite inferior da integral.
        b (float): Limite superior da integral.
        n (int): Número de divisões do intervalo de integração. Valor padrão é 100.
        mostrar_grafico (bool, optional): Define se deve gerar o gráfico ou não. Valor padrão é False.
        precisao (int, optional): Número de casas decimais no resultado retornado. Se None, não arredonda.
        metodo (str, optional): Método escolhido para a integração. Valor padrão é 'Trapezoidal'.

    Raises:
        ValueError: Se o método escolhido não estiver entre os implementados.

    Returns:
        float: Valor numérico obtido para a integral arredondado 
        de acordo com a precisão, caso fornecida.
    """

    metodo = metodo.capitalize()

    if metodo not in metodos_integral:
        raise ValueError(
            f"Erro: o método escolhido é inválido. "
            f"Os métodos válidos são {', '.join(metodos_integral.keys())}"
        )

    funcao_escolhida = metodos_integral[metodo]
    return funcao_escolhida(funcao, a, b, n, mostrar_grafico, precisao)


if __name__ == "__main__":
    funcao1 = lambda x: np.sin(x)
    funcao2 = lambda x: np.sin(3*x)
    a = 0
    b = np.pi
    '''número de pontos para a curva suave'''
    # s = 100 
    ''' n = número de partições de trapézios'''
    area1 = integral(funcao1, a, b, n=3, mostrar_grafico=True, metodo='Trapezoidal')
    print(area1)
    area2 = integral(funcao1, a, b, n=3, mostrar_grafico=True, metodo='Simpson')
    print(area2)
    area3 = integral(funcao2, a, b, n=4, mostrar_grafico=True, metodo='Trapezoidal')
    print(area3)
    area4 = integral(funcao2, a, b, n=4, mostrar_grafico=True, metodo='Simpson')
    print(area4)
    # grafico(funcao, a, b, s, area, n=20)
