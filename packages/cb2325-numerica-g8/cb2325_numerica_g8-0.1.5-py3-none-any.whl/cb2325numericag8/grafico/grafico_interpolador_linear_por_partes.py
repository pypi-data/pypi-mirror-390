import numpy as np
import matplotlib.pyplot as plt

def grafico_interpolacao_linear(interpolador, a=None, b=None, s=400):
    """
    Exibe o gráfico da interpolação linear por partes.

    Args:
        interpolador (InterpolacaoLinearPorPartes): Objeto da classe InterpolacaoLinearPorPartes.
        a (float, optional): Limite inferior do gráfico. Se None, usa o menor x dos dados.
        b (float, optional): Limite superior do gráfico. Se None, usa o maior x dos dados.
        s (int, optional): Número de pontos para suavização das linhas (densidade do gráfico).
    """
    plt.style.use('seaborn-v0_8-whitegrid')

    # Limites de plotagem
    if a is None:
        a = min(interpolador.x)
    if b is None:
        b = max(interpolador.x)

    # Gera pontos para o gráfico
    x_plot = np.linspace(a, b, s)
    y_plot = [interpolador(xi) for xi in x_plot]

   # Pontos de base
    plt.scatter(interpolador.x, interpolador.y,
                color='blue', s=60, zorder=3,edgecolors='black',
                 linewidths=1.0,  label='Pontos Originais (x, f(x))')

    # Linhas lineares por partes
    plt.plot(x_plot, y_plot,
             color='crimson', linewidth=2.2, zorder=2,
             label='Interpolação Linear por Partes')

    # Linhas verticais pontilhadas indicando subintervalos
    for xi in interpolador.x:
        plt.axvline(xi, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)

    # Configurações estéticas
    plt.title('Interpolação Linear por Partes', fontsize=14, fontweight='bold')
    plt.xlabel('Eixo X', fontsize=12)
    plt.ylabel('Eixo Y', fontsize=12)
    plt.legend(loc='best', frameon=True, shadow=True)
    plt.tight_layout()
    plt.show()
