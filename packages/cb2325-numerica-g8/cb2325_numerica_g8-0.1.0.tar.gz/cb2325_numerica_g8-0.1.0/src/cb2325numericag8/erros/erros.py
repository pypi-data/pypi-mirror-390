from cb2325numericag8.utils.kahan import soma_kahan


def erro_absoluto(v_real, v_aproximado, precisao=None):
    """
    Retorna o erro absoluto para um valor de referência dado e um valor obtido.

    Args:
        v_real (float): Valor teórico de referência.
        v_aproximado (float): Valor obtido para comparação.
        precisao (int, optional): Número de casas decimais no resultado retornado.

    Raises:
        ValueError: Se um dos valores fornecidos não for numérico.

    Returns:
        float: Erro absoluto arredondado de acordo com a precisão, caso fornecida.
    """

    try:
        v_real = float(v_real)
        v_aproximado = float(v_aproximado)
    except ValueError:
        raise ValueError("Erro: os valores real e aproximado devem ser numéricos.")
    erro = abs(v_real - v_aproximado)
    if precisao is not None:
        return round(erro, precisao)
    return erro


def erro_relativo(v_real, v_aproximado, precisao=None):
    """
    Retorna o erro relativo para um valor de referência dado e um valor obtido.

    Args:
        v_real (float): Valor teórico de referência, deve ser diferente de zero.
        v_aproximado (float): Valor obtido para comparação.
        precisao (int, optional): Número de casas decimais no resultado retornado.

    Raises:
        ValueError: Se um dos valores fornecidos não for numérico.
        ValueError: Se o valor real for zero.

    Returns:
        float: Erro relativo arredondado de acordo com a precisão, caso fornecida.
    """

    try:
        v_real = float(v_real)
        v_aproximado = float(v_aproximado)
    except ValueError:
        raise ValueError("Erro: os valores real e aproximado devem ser numéricos.")
    if v_real == 0:
        raise ValueError(
            "Erro: o valor real não pode ser zero para o cálculo do erro relativo."
        )
    erro = abs((v_real - v_aproximado) / v_real)
    if precisao is not None:
        return round(erro, precisao)
    return erro


def erro_quadratico_medio(lista_real, lista_aproximada, precisao=None):
    """
    Retorna o erro quadrático médio para uma lista de valores de referência 
    e uma lista de valores obtidos.

    Args:
        lista_real (list of float): Valores teóricos de referência.
        lista_aproximada (list of float): Valores obtidos para comparação.
        precisao (int, optional): Número de casas decimais no resultado retornado.

    Raises:
        ValueError: Se as listas não possuírem o mesmo tamanho.
        ValueError: Se as listas forem vazias.
        ValueError: Se um dos valores fornecidos não for numérico.
        
    Returns:
        float: Erro quadrático médio arredondado de acordo com a precisão, caso fornecida.
    """

    if len(lista_real) != len(lista_aproximada):
        raise ValueError("Erro: as listas devem possuir a mesma quantidade de elementos.")
    n = len(lista_real)
    if n == 0:
        raise ValueError("Erro: as listas não podem ser vazias.")
    try:
        valores_reais = [float(v) for v in lista_real]
        valores_aproximados = [float(v) for v in lista_aproximada]
    except ValueError:
        raise ValueError("Erro: todos os valores das listas devem ser numéricos.")
    lista_erros_quadraticos = [(real - aproximado) ** 2 for real, aproximado 
                               in zip(valores_reais, valores_aproximados)]
    eqm = soma_kahan(lista_erros_quadraticos) / n
    if precisao is not None:
        return round(eqm, precisao)
    return eqm
