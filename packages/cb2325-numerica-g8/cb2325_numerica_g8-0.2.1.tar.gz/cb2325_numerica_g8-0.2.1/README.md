# 📈 Cálculo Numérico

Este repositório contém implementações de métodos de integração numérica, interpolação, raízes e cálculo de erros, desenvolvidos para a disciplina de programação 2 do IMPA TECH.

---

## 🚀 Funcionalidades

Este projeto implementa as seguintes funcionalidades:

* **Cálculo de Erros:**
    * Erro Absoluto;
    * Erro Relativo;
    * Erro Quadrático Médio.

* **Interpolação:**
    * Interpolação Polinomial;
    * Interpolação de Hermite;
    * Interpolação Linear por partes.

* **Raízes de Funções:**
    * Método da Bisseção;
    * Método da Secante;
    * Método de Newton-Raphson.

* **Integração Numérica:**
    * Método do Trapézio;
    * Método de Simpson.
---

## 📋 Pré-requisitos

Para executar este projeto, você precisará de:

* Python 3.9+
* NumPy
* Matplotlib

---

## 💡 Exemplo de Uso


### Cálculo de erros
Aqui estão exemplos de como usar os métodos de cálculo de erros.

#### Erro absoluto
```python
# 1. Defina os valores de entrada
valor_teorico = 3.1415926
valor_aproximado = 3.14

# 2. Defina uma precisão (opcional)
p = 3

# 3. Realize a chamada da função
erro1 = erro_absoluto(valor_teorico, valor_aproximado)
erro2 = erro_absoluto(valor_teorico, valor_aproximado, precisao=p)

# 4. Saída esperada
print(erro1)
print(erro2)
```
#### Erro relativo
```python
# 1. Defina os valores de entrada
valor_teorico = 3.1415926
valor_aproximado = 3.14

# 2. Defina uma precisão (opcional)
p = 3

# 3. Realize a chamada da função
erro1 = erro_relativo(valor_teorico, valor_aproximado)
erro2 = erro_relativo(valor_teorico, valor_aproximado, precisao=p)

# 4. Saída esperada
print(erro1)
print(erro2)
```
#### Erro quadrático médio
```python
# 1. Defina os valores de entrada (listas)
valores_teoricos = [3.1415926, 2.7182818]
valores_aproximados = [3.14, 2.72]

# 2. Defina uma precisão (opcional)
p = 3

# 3. Realize a chamada da função
erro1 = erro_quadratico_medio(valores_teoricos, valores_aproximados)
erro2 = erro_quadratico_medio(valores_teoricos, valores_aproximados, precisao=p)

# 4. Saída esperada
print(erro1)
print(erro2)
```
### Interpoladores
Aqui estão exemplos de como usar os interpoladores.

#### Interpolação de Hermite

```python
# 1. Defina os dados de entrada
pontos_x = [0, 1]
valores_y = [1, 2]
derivadas_dy = [1, 0]

# 2. Crie uma instância da class
polinomio = InterpoladorHermite(pontos_x, valores_y, derivadas_dy)

# 3. Ache o valor desejado para um ponto
print(f"H(0) = {polinomio(0):.4f}")
print(f"H(1) = {polinomio(1):.4f}")
print(f"H(0.5) = {polinomio(0.5):.4f}")
```
#### Interpolação Linear por Partes

```python
# 1. Defina os dados de entrada
valores_x = [1, 2, 3, 4, 6]
valores_y = [2, 4, 8, 16, 64]

# 2. Crie uma instância da classe
teste_linear = InterpolacaoLinearPorPartes(valores_x,valores_y)

# 3. Interpole um ponto
print(f"L(5) = {teste_linear(5):.4f}")

# 4. Interpole muitos pontos
teste_linear.calcular_retas()
x_k = 1
for i in range(50):
    print(f"L({x_k:.2f})= {teste_linear.interpolar_muitos_pontos(x_k):.2f}")
    x_k += 0.1
```
#### Interpolação Polinomial

```python
# 1. Defina os dados de entrada
pontos_x = [0, 1, 3, 4]
valores_y = [0, 0, 6, 12]

# 2. Crie uma instância da class
polinomio = InterpoladorPolinomial(pontos_x, valores_y)

# 3. Ache o valor desejado para um ponto
i = 0
while i < 10.5:
    print(f"H({i}) = {polinomio(i):.4f}")
    i += 0.5
```
### Raízes
Aqui estão exemplos de como usar os métodos raízes de funções.

#### Método da Bisseção 

```python
#1. Defina a função de entrada 
def f(x):
    return x**2 - 2

#2. Utilizar o método na função de entrada
raiz0,_ = raiz(f, a=0, b=2, tol=1e-6, method="bissecao")

#3. Saída esperada
print(raiz0)
```
#### Método da Secante

```python
#1. Defina a função de entrada
def g(x):
    return x**3 - 9*x + 5

#2. Utilizar o método na função de entrada
raiz1,_ = raiz(g, a=0, b=2, tol=1e-6, method="secante")

#3. Saída esperada
print(raiz1)
```
#### Método de Newton-Raphson

```python
#1. Defina as funções de entrada
def h(x):
     return x**10 - 5

def h_prime(x):
     return 10 * x**9

#2. Utilizar o método nas funções de entrada
raiz2,_ = raiz(h, a=2, f_prime=h_prime, tol=1e-6, method="newton_raphson")

#3. Saída esperada
print(raiz2)
```

### Integração Numérica
Aqui estão exemplos de como usar os métodos de integração numérica.
```python
# 1. Defina a função a ser integrada
def funcao1(x):
    return x**2
funcao2 = lambda x: x**2

# 2. Defina o intervalo de integração
limite_inferior = 0
limite_superior = 3.14

# 3. Defina o número de subdivisões de intervalo de integração, precisão e se deseja exibir o gráfico (opcionais)
subdivisoes = 100
p = 3
exibir = True

# 4. Defina o método (opcional)
metodo1 = "Trapezoidal"
metodo2 = "Simpson"

# 5. Realize a chamada da função
area1 = integral(funcao1, a, b, n=subdivisoes, mostrar_grafico=exibir, metodo=metodo1, precisao=p)
area2 = integral(funcao1, a, b, metodo=metodo2)
area3 = integral(funcao1, a, b)
area4 = integral(funcao2, a, b)

# 6. Saída esperada: gráfico (para area1) e valores
print(area1)
print(area2)
print(area3)
print(area4)
```

### Regressão Linear
```python
# 1. Defina os pontos (dados experimentais)
x = [0, 1, 2, 3, 4, 5]
y = [2.1, 2.9, 4.2, 5.1, 6.8, 8.0]

# 2. Defina o grau do polinômio (opcional)
grau1 = 1   # Ajuste linear
grau2 = 2   # Ajuste quadrático

# 3. Defina se deseja exibir o gráfico (opcional)
exibir = True

# 4. Realize a chamada da função
ajuste1 = aproximacao_polinomial(x, y, grau=grau1, mostrar_grafico=exibir)
ajuste2 = aproximacao_polinomial(x, y, grau=grau2)

# 5. Saída esperada: gráfico (para ajuste1) e coeficientes
print(ajuste1)
print(ajuste2)
```
### Representação Gráfica

Aqui estão exemplos de como usar as funções de representação gráfica.

#### Interpoladores

##### Interpolação de Hermite
```python
# 1. Definimos os pontos conhecidos e suas derivadas
valores_x = [0, 1, 2]
valores_y = [1, 3, 2]
valores_y_deriv = [1, 0, -1]

# 2. Criamos o interpolador de Hermite
interpolador = InterpoladorHermite(valores_x, valores_y, valores_y_deriv)

# 3. Avaliamos o polinômio em um ponto
x_avaliar = 1.5
print(f"H({x_avaliar}) =", interpolador(x_avaliar))

# 4. Geramos o gráfico do polinômio interpolador de Hermite
interpolador.grafico()

```
##### Interpolação Linear por Partes 
```python
# 1. Definimos os pontos conhecidos
valores_x = [1, 2, 3, 5]
valores_y = [2, 4, 8, 32]

# 2. Criamos o interpolador linear por partes
interpolador = InterpolacaoLinearPorPartes(valores_x, valores_y)

# 3. Avaliamos o interpolador em um ponto
x_avaliar = 4
print(f"f({x_avaliar}) =", interpolador(x_avaliar))

# 4. Geramos o gráfico da interpolação linear por partes
interpolador.grafico()
```
##### Interpolação Polinomial
```python
# 1. Definimos os pontos conhecidos
valores_x = [0, 1, 2, 3]
valores_y = [1, 2, 0, 5]

# 2. Criamos o interpolador de Newton
interpolador = InterpoladorPolinomial(valores_x, valores_y)

# 3. Avaliamos o polinômio em um ponto
x_avaliar = 1.5
print(f"P({x_avaliar}) =", interpolador(x_avaliar))

# 4. Geramos o gráfico do polinômio interpolador
interpolador.grafico()
```

#### Raízes
```python
# 1. Definimos a função cuja raiz queremos encontrar
f = lambda x: x**3 - 9*x + 5

# 2. Escolhemos um intervalo ou estimativas iniciais
a = 0
b = 2

# 3. Aplicamos o método escolhido (por exemplo, o método da Secante)
raiz_aproximada, iteracoes = raiz(f, a=a, b=b, tol=1e-6, method="secante")

# 4. Exibimos o valor aproximado da raiz
print(f"Raiz aproximada: {raiz_aproximada:.6f}")

# 5. Geramos o gráfico com as iterações e a função
grafico(f, iteracoes, a, b, titulo_metodo="Método da Secante")
```
#### Integração Numérica

```python
# 1. Definimos a função
def f(x):
    return x**2

# 2. Realize a integração pelo método dos trapézios
area_trap = integral(f, 0, 3, n=20, metodo='Trapezoidal', mostrar_grafico=True)
print("Área (Trapézios) =", area_trap)

# 3. Realize a integração pelo método de Simpson
area_simp = integral(f, 0, 3, n=20, metodo='Simpson', mostrar_grafico=True)
print("Área (Simpson) =", area_simp)
```

#### Aproximação

##### Regressão Linear
```python
# 1. Definimos os dados experimentais
x = [0, 1, 2, 3, 4]
y = [1.1, 1.9, 3.0, 3.9, 5.2]

# 2. Calculamos os coeficientes da reta ajustada
a, b = ajuste_linear(x, y)

# 3. Exibimos a equação da reta
print(f"Equação ajustada: y = {a:.2f}x + {b:.2f}")

# 4. Geramos o gráfico do ajuste linear
grafico_ajuste_linear(x, y, a, b)
```

##### Mínimos Quadrados
```python
# 1. Definimos os pontos de entrada (x, y)
x = [0, 1, 2, 3, 4]
y = [1, 2.2, 2.8, 3.6, 5.1]

# 2. Chamamos a função de Aproximação Polinomial
coef = AproximacaoPolinomial(x, y, grau=2, plot=True)

# 3. Exibimos os coeficientes do polinômio ajustado
print("Coeficientes do polinômio aproximado:", coef)
```

