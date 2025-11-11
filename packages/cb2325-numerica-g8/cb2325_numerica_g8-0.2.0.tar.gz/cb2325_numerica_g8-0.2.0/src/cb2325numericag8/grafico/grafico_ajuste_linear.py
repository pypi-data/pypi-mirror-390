import numpy as np
import matplotlib.pyplot as plt

def grafico_ajuste_linear(x, y, a, b):
    """
    Exibe o gráfico do ajuste linear (Regressão Linear).

    Args:
        x (list or array): Valores originais de x.
        y (list or array): Valores observados correspondentes.
        a (float): Coeficiente angular da reta ajustada.
        b (float): Coeficiente linear da reta ajustada.
    """
    plt.style.use('seaborn-v0_8-whitegrid')

    # Constrói reta ajustada com base nos coeficientes
    x_suave = np.linspace(min(x), max(x), 300)
    y_suave = a * x_suave + b

    # Plota os pontos originais
    plt.scatter(x, y, s=60,facecolor='blue',edgecolor='black',        
        linewidth=0.8, zorder=3,label='Pontos Reais')

    # Plota a reta ajustada
    plt.plot(x_suave, y_suave, color='crimson', linewidth=2.2,
             label=f'Reta Ajustada: y = {a:.2f}x + {b:.2f}', zorder=2)

    # Configurações visuais
    plt.title("Ajuste Linear (Regressão Linear)", fontsize=14, fontweight='bold')
    plt.xlabel("Eixo X", fontsize=12)
    plt.ylabel("Eixo Y", fontsize=12)
    plt.legend(loc='best', frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
