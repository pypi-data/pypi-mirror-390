import numpy as np
import matplotlib.pyplot as plt

def grafico_hermite(interpolador, a=None, b=None, s=300):
    """
    Exibe o gráfico da interpolação de Hermite.

    Args:
        interpolador (InterpoladorHermite): Objeto da classe InterpoladorHermite.
        a (float, optional): Limite inferior do gráfico. Se None, usa o menor x dos dados.
        b (float, optional): Limite superior do gráfico. Se None, usa o maior x dos dados.
        s (int, optional): Número de pontos para suavização da curva.
    """
    plt.style.use('seaborn-v0_8-whitegrid')

    # Definição do intervalo de plotagem
    if a is None:
        a = min(interpolador.valorx)
    if b is None:
        b = max(interpolador.valorx)

    # Gera pontos suaves para a curva
    x_suave = np.linspace(a, b, s)
    y_suave = [interpolador(xi) for xi in x_suave]

    # Pontos reais e derivadas
    plt.scatter(interpolador.valorx, interpolador.valory,
                color='blue', label='Pontos (x, f(x))', s=60,
                 markersize=5, markercolor='black', zorder=3)

    # Curva interpoladora de Hermite
    plt.plot(x_suave, y_suave, color='crimson', linewidth=2.2,
             label='Polinômio de Hermite', zorder=2)

    # Linhas indicativas das derivadas nos pontos
    for xi, yi, dy in zip(interpolador.valorx, interpolador.valory, interpolador.valory_deriv):
        plt.arrow(xi, yi, 0.15, 0.15 * dy,
                  color='yellow', width=0.002, head_width=0.05,
                  length_includes_head=True, alpha=0.6)

    plt.title("Interpolação de Hermite", fontsize=14, fontweight='bold')
    plt.xlabel("Eixo X", fontsize=12)
    plt.ylabel("Eixo Y", fontsize=12)
    plt.legend(loc='best',frameon=True, shadow=True)
    plt.tight_layout()
    plt.show()
