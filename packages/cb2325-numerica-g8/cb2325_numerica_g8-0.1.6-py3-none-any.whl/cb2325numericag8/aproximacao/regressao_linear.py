import matplotlib.pyplot as plt

def ajuste_linear(x, y, plot=True):
    """
    Calcula o ajuste linear dos dados (mínimos quadrados).

    Parâmetros:
    x, y : listas ou arrays numéricos
    plot : bool (opcional)
        Se True, mostra o gráfico dos pontos e da reta ajustada.

    Retorna:
    a, b : coeficientes da reta ajustada (y = a*x + b)
    """
    n = len(x)
    soma_x = sum(x)
    soma_y = sum(y)
    soma_xy = sum(xi * yi for xi, yi in zip(x, y))
    soma_x2 = sum(xi**2 for xi in x)

    a = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x**2)
    b = (soma_y - a * soma_x) / n

    if plot:
        plt.scatter(x, y, color='blue', label='Pontos reais')
        plt.plot(x, [a*xi + b for xi in x], color='red', label=f'y = {a:.2f}x + {b:.2f}')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.title('Ajuste Linear (Mínimos Quadrados)')
        plt.grid(True)
        plt.show()

    return a, b

# Exemplo de uso
if __name__ == "__main__":
    x = [0, 1, 2, 3, 4]
    y = [1.1, 1.9, 3.0, 3.9, 5.2]
    a, b = ajuste_linear(x, y)
    print(f"y = {a:.2f}x + {b:.2f}")
