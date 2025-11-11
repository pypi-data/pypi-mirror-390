import numpy as np
import matplotlib.pyplot as plt

def plot_aproximacao(x_pontos, y_pontos, coeficientes, n_suave=500):
    """
    Gera um gráfico dos pontos de entrada e do polinômio de aproximação.

    Args:
        x_pontos (list ou array): Coordenadas x de entrada.
        y_pontos (list ou array): Coordenadas y de entrada.
        coeficientes (list): Coeficientes do polinômio (maior para menor grau).
        n_suave (int, optional): Número de pontos para a curva suave.
                                 Padrão é 500.
    """
    plt.style.use('seaborn-v0_8-darkgrid') 
    
    x_min = np.min(x_pontos)
    x_max = np.max(x_pontos)
    x_suave = np.linspace(x_min, x_max, n_suave)

    y_suave = np.polyval(coeficientes, x_suave)

    #Curva Suvae
    plt.plot(x_suave, y_suave, 
             '-', 
             label="Aproximação por Mínimos Quadrados", 
             color='crimson', 
             linewidth=2,
             zorder=2)

    #Pontos de Entrada        
    plt.plot(x_pontos, y_pontos, 
             'o', 
             label="Pontos de Entrada", 
             color='blue', 
             markersize=7, 
             markeredgecolor='black',
             zorder=3)

    plt.title("Gráfico da Aproximação Polinomial (Mínimos Quadrados)", 
              fontsize=14, fontweight='bold')
    plt.xlabel("Eixo X", fontsize=12)
    plt.ylabel("Eixo Y", fontsize=12)
    plt.legend(loc='best', frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.show()
