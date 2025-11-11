#Implementação do método das raízes

from cb2325numericag8.grafico.grafico_raizes import grafico

def raiz(funcao, a, b=None, f_prime=None, tol=1e-6, max_iter=1000, method="secante", mostrar_grafico=False):
    """
    Função principal para encontrar raizes de uma equação f(x)=0.

    Args:
        funcao (callable): expressão dada para a função f(x)
        a (float): parâmetro inicial (depende do método escolhido)
        b (float): parâmetro inicial (depende do método escolhido)
        tol (float): tolerância para a convergência do método.
        f_prime (callable): derivada da função f(x).
        max_iter (int): número máximo de iterações do método.
        method (str): método a ser utilizado.
        mostrar_grafico (bool): se for True plota o gráfico. Padrão é False.
    
    Returns:
        tuple (float, list): raiz encontrada e lista de iterações.
    
    Raises:
        ValueError: Se o método não for reconhecido.
    """

    if method == "bissecao":
        raiz,lista_iteracoes=bissecao(funcao, a, b, tol, max_iter)
        if(mostrar_grafico==True):
            grafico(funcao, lista_iteracoes, titulo_metodo="Método Numérico da Bisseção para Raízes")
        return raiz,lista_iteracoes

    elif method == "secante":
        raiz,lista_iteracoes=secante(funcao, a, b, tol, max_iter)
        if(mostrar_grafico==True):
            grafico(funcao, lista_iteracoes, titulo_metodo="Método Numérico da Secante para Raízes")
        return raiz,lista_iteracoes

    elif method == "newton_raphson":
        raiz,lista_iteracoes=newton(funcao, a, f_prime,tol, max_iter)
        if(mostrar_grafico==True):
            grafico(funcao, lista_iteracoes, titulo_metodo="Método Numérico de Newton-Raphson para Raízes")
        return raiz,lista_iteracoes
    
    else:
        raise ValueError("Método não reconhecido")

def bissecao(funcao, a, b, tol, max_iter):
    """
    Encontra a raiz de uma equação f(x)=0 usando o método da bisseção.

    Este método requer um intervalo inicial [a, b] tal que f(a) e f(b)
    tenham sinais opostos (Teorema de Bolzano).

    Args:
        funcao (callable): expressão dada para a função f(x).
        a (float): limite inferior do intervalo de busca.
        b (float): limite superior do intervalo de busca.
        tol (float): tolerância para a convergência do método.
        max_iter (int): número máximo de iterações do método.
    
    Returns:
        tuple (float, list): raiz encontrada e lista de iterações.
    
    Raises:
        ValueError: Se f(a) e f(b) têm o mesmo sinal.
        RuntimeError: Se o número máximo de iterações
                      é atingido sem convergência.
    """

    f_a = funcao(a)
    f_b = funcao(b)

    if f_a*f_b > 0:
        raise ValueError(
            "Erro: f(a) e f(b) têm o mesmo sinal."
            "O método não pode garantir uma raiz no intervalo."
            )
    
    elif f_a == 0:
        return a, [a]
    elif f_b == 0:
        return b, [b]
    
    else:
        iter = 0
        iter_para_plot = []

        while (b-a)/2 > tol and iter < max_iter:
            m = (a+b)/2
            f_m = funcao(m)
            iter_para_plot.append(m)
            iter += 1

            if f_m == 0:
                break

            if f_a*f_m < 0:
                b = m
                f_b = f_m
            else:
                a = m
                f_a = f_m
        if (b-a)/2 > tol and iter == max_iter:
            raise RuntimeError("Número máximo de iterações atingido sem convergência.")
        else: 
            return (a+b)/2, iter_para_plot

def secante(funcao, a, b, tol, max_iter):
    """
    Encontra a raiz de uma equação f(x)=0 usando o método da secante.

    Este método requer duas estimativas iniciais a e b para o valor da
    raiz, tal que f(a) é diferente de f(b).

    Args:
        funcao (callable): expressão dada para a função f(x).
        a (float): aproximação inicial para a raiz
        b (float): aproximação inicial para a raiz
        tol (float): tolerância para a convergência do método.
        max_iter (int): número máximo de iterações do método.
    
    Returns:
        tuple (float, list): raiz encontrada e lista de iterações.
    
    Raises:
        ZeroDivisionError: Se f(a) e f(b) são iguais.
        RuntimeError: Se o número máximo de iterações
                      é atingido sem convergência.
    """

    iter = 0
    iter_para_plot = []
    f_a = funcao(a)
    f_b = funcao(b)

    while iter < max_iter:

        if (f_a - f_b == 0):
            raise ZeroDivisionError("Erro: f(a) - f(b) = 0. Divisão por zero.")
        
        c = b - f_b*((b-a) / (f_b-f_a))
        f_c = funcao(c)
        iter_para_plot.append(c)

        if (abs(c-b) < tol or abs(f_c) < tol):
            return c, iter_para_plot
        a = b
        f_a = f_b
        b = c
        f_b = f_c
        iter += 1
    raise RuntimeError("Número máximo de iterações atingido sem convergência.")


def newton(funcao, a, f_prime, tol, max_iter):
    """
    Encontra a raiz de uma equação f(x)=0 usando o método de newton-raphson.

    Este método requer uma estimativa inicial a para o valor da raiz e a 
    derivada f_prime da função

    Args:
        funcao (callable): expressão dada para a função f(x).
        a (float): aproximação inicial para a raiz
        f_prime (callable): expressão dada para a função f'(x).
        tol (float): tolerância para a convergência do método.
        max_iter (int): número máximo de iterações do método.
    
    Returns:
        tuple: raiz encontrada e lista de iterações.
    
    Raises:
        ZeroDivisionError: Se f'(a) = 0.
        RuntimeError: Se o número máximo de iterações
                      é atingido sem convergência.
    """

    iter = 0
    iter_para_plot = []

    if (f_prime == None):
            h=tol
            f_prime=lambda x: (funcao(x+h)-funcao(x))/h
            
    while iter < max_iter:
        f_a = funcao(a)
        f_prime_a=f_prime(a)

        if f_prime_a == 0:
            raise ZeroDivisionError("Erro: derivada zero f_prime(a) = 0. Divisão por zero.")
        
        c = a - f_a/f_prime_a
        iter_para_plot.append(c)
        
        if (abs(c-a) < tol and abs(funcao(c))<tol):
            return c, iter_para_plot
        
        a = c
        iter += 1
    
    raise RuntimeError("Número máximo de iterações atingido sem convergência.")
