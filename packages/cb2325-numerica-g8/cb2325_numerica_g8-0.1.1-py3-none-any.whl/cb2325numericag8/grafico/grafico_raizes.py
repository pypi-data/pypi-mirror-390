import numpy as np
import matplotlib.pyplot as plt

def grafico(funcao, iteracoes, a=None, b=None, titulo_metodo="Método Numérico para Raízes"):
    """
    Exibe o gráfico da função f(x) e as aproximações sucessivas do método.

    Args:
        funcao (callable): Função f(x) usada para encontrar a raiz.
        iteracoes (list): Lista das aproximações geradas durante o método.
        a (float, optional): Limite inferior do intervalo exibido no gráfico.
        b (float, optional): Limite superior do intervalo exibido no gráfico.
        titulo_metodo (str, optional): Título a ser exibido no gráfico.
    """
    plt.style.use('seaborn-v0_8-whitegrid')

    # Define os limites de plotagem
    if a is None:
        a = min(iteracoes) - 1
    if b is None:
        b = max(iteracoes) + 1

    # Cria uma faixa de valores para a curva da função
    x_vals = np.linspace(a, b, 500)
    y_vals = np.array([funcao(x) for x in x_vals])

    # Plota a curva principal f(x)
    plt.plot(x_vals, y_vals, label="f(x)", color="#2255A4", linewidth=2.5)

    # Marca o eixo x
    plt.axhline(0, color='black', linewidth=0.8)

    # Marca os pontos de iteração
    y_iter = [funcao(x) for x in iteracoes]
    plt.scatter(iteracoes, y_iter, color='crimson', s=60, zorder=3, label='Iterações')

    # Liga as iterações por linhas tracejadas
    plt.plot(iteracoes, y_iter, color='crimson', linestyle='--', alpha=0.8)

    # Destaca a última aproximação (raiz final)
    plt.scatter(iteracoes[-1], funcao(iteracoes[-1]), color='green', s=80, zorder=4, label='Raiz Aproximada')

    # Configurações estéticas
    plt.title(titulo_metodo, fontsize=14, fontweight='bold')
    plt.xlabel("Eixo X", fontsize=12)
    plt.ylabel("f(x)", fontsize=12)
    plt.legend(frameon=True, shadow=True)
    plt.tight_layout()
    plt.show()
