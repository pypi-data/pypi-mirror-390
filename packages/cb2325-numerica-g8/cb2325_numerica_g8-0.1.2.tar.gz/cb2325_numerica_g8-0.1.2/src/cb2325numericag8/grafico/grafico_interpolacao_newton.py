import numpy as np
import matplotlib.pyplot as plt

def plot(self, num_pontos_suavizacao: int = 500):
        """
        Gera um gráfico do polinômio de interpolação e dos pontos de entrada.

        Args:
            num_pontos_suavizacao (int, optional): Número de pontos para
                                                   a curva suave.
                                                   Padrão é 500.

        Returns:
            None. Exibe um gráfico do Matplotlib.
        """

        plt.style.use('seaborn-v0_8-darkgrid')

        x_min = np.min(self.valores_x)
        x_max = np.max(self.valores_x)
        x_suave = np.linspace(x_min, x_max, num_pontos_suavizacao)

        # A primeira chamada de self(x) irá preencher o cache.
        # As chamadas subsequentes serão rápidas.
        y_suave = [self(x) for x in x_suave]

        plt.plot(x_suave, y_suave,
                 '-',
                 label="Polinômio de Interpolação",
                 color='orange',
                 linewidth=2,
                 zorder=2)

        plt.plot(self.valores_x, self.valores_y,
                 'o',
                 label="Pontos de Entrada",
                 color='blue',
                 markersize=7,
                 markeredgecolor='black',
                 zorder=3)

        plt.title("Gráfico do Polinômio de Interpolação de Newton",
                  fontsize=14, fontweight='bold')
        plt.xlabel("Eixo X", fontsize=12)
        plt.ylabel("Eixo Y", fontsize=12)
        plt.legend(loc='best', frameon=True, shadow=True)
        plt.grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.show()
