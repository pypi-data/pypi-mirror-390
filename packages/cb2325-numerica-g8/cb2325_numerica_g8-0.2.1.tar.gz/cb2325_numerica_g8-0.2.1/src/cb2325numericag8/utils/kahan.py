def soma_kahan(lista):
    """
    Aplica o algoritmo de soma de Kahan para somar todos os elementos 
    de uma lista, a fim de evitar erros de ponto flutuante.

    Args:
        lista (list): Lista com os números a serem somados.

    Returns:
        float: Valor numérico obtido para a soma.
    """

    soma = 0.0
    c = 0.0 # Variável de compensação
    
    for valor in lista:
        y = valor - c
        t = soma + y
        c = (t - soma) - y
        soma = t

    return soma