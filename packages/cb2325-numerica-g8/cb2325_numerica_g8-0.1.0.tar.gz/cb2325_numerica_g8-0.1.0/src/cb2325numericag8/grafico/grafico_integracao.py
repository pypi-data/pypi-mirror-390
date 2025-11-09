import numpy as np
import matplotlib.pyplot as plt

def grafico(funcao, a, b, s, area, n=20):
    """
    Gera e exibe um gráfico da função e da área aproximada da integral.

    Args:
        funcao (callable): A função a ser plotada.
        a (float): Limite inferior da integral.
        b (float): Limite superior da integral.
        s (int): Número de pontos para a curva suave.
        area (float): Valor numérico da área da integral aproximada.
        n (int, optional): Número de partições do trapézio. 
                           Valor padrão é 20.

    Returns:
        None: Exibe o gráfico utilizando plt.show().
    """
    
    plt.style.use('seaborn-v0_8-whitegrid')

    # Dados curva suave
    x_curva = np.linspace(a, b, s)
    y_curva = funcao(x_curva)

    # Vértices do trapézio (pontos discretos)
    x_disc = np.linspace(a, b, n + 1)
    y_disc = funcao(x_disc)
    
    plt.plot(x_curva, y_curva, label="f(x)", color="#2255A4", 
             linewidth=2.5, alpha=0.9) 
    
    plt.fill_between(x_disc, y_disc, 0, label="Área da Aproximação", 
                     color="skyblue", alpha=0.6)
    
    plt.vlines(x_disc, 0, y_disc, color="red", linestyle="--", 
               linewidth=0.8, alpha=0.7)
    plt.plot(x_disc, y_disc, color="red", linewidth=1.5, alpha=0.8)
    
    plt.plot(x_disc, y_disc, 'o', color='darkred', markersize=5, 
             label=f'{n} Partições')
    

    plt.axhline(0, color='black', linewidth=0.5)

    plt.title(f"Aproximação da Integral ≈ {area:.4f}", 
              fontsize=14, fontweight='bold')
    plt.xlabel("Eixo X", fontsize=12)
    plt.ylabel("Eixo Y", fontsize=12)

    plt.legend(loc='upper left', frameon=True, shadow=True)

    plt.tight_layout()

    return plt.show()
