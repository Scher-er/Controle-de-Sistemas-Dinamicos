# Seu Amigo de Todas as Horas ⚙️

O **Seu Amigo de Todas as Horas** é uma ferramenta completa de Engenharia de Controle e Automação desenvolvida em Python. O software foi projetado para auxiliar estudantes e profissionais na análise de sistemas dinâmicos, oferecendo desde a simplificação de diagramas de blocos até a análise detalhada de estabilidade e erro em regime permanente.



---

## 🚀 Funcionalidades

O software é dividido em módulos especializados, acessíveis através de um dashboard intuitivo:

1.  **🧩 Álgebra de Blocos:** Deduza a Função de Transferência (FT) de malha fechada a partir de $G(s)$ e $H(s)$, com suporte a realimentação positiva e negativa.
2.  **📊 Tabela de Routh-Hurwitz:** Analise a estabilidade absoluta de sistemas e determine faixas de ganho $K$ para estabilidade marginal através de cálculos simbólicos exatos.
3.  **📈 Resposta ao Degrau:** Gere gráficos de comportamento temporal para verificar o regime transitório de qualquer sistema linear e invariante no tempo (LTI).
4.  **∫ Laplace Inversa:** Converta funções no domínio de Laplace $F(s)$ para o domínio do tempo $f(t)$ com simplificação automática de frações parciais.
5.  **🎯 Erro e Transitório:** Identifique o Tipo do Sistema (0, 1 ou 2) e calcule constantes de erro ($K_p$, $K_v$, $K_a$) e parâmetros de desempenho ($\zeta$, $\omega_n$, $T_r$, $T_p$, $M_p$, $T_s$).
6.  **📍 Lugar das Raízes (LGR):** Extraia parâmetros fundamentais para o esboço do LGR, incluindo centroide, ângulos das assíntotas e pontos de quebra.
7.  **📐 Avaliação Complexa:** Avalie o módulo e a fase de $F(s)$ em qualquer ponto complexo $s = \sigma + j\omega$.
8.  **📚 Fórmulas Essenciais:** Guia de consulta rápida com as principais equações da teoria de controle moderno.

---

## 🛠️ Tecnologias e Dependências

O projeto utiliza as seguintes bibliotecas de Python:

* **CustomTkinter:** Interface gráfica moderna com suporte a modo escuro.
* **SymPy:** Motor de álgebra simbólica para cálculos exatos e transformadas.
* **SciPy & NumPy:** Processamento numérico e simulação de sistemas de controle.
* **Matplotlib:** Plotagem de gráficos e visualização de dados.

---

## 📥 Instalação

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.8+** instalado em sua máquina.

### 2. Instalação das Bibliotecas
Abra o seu terminal (ou CMD) e execute o seguinte comando para instalar todas as dependências necessárias:

pip install customtkinter sympy scipy matplotlib numpy

### 3. Gerando o Executável (Opcional)
Se desejar transformar o script em um software independente (.exe), instale o PyInstaller:

pip install pyinstaller
E execute o comando de compilação:

pyinstaller --noconsole --onefile app.py

## 🖥️ Como Usar
Execute o arquivo app.py ou o executável gerado.

Na tela inicial, clique na mensagem de boas-vindas para acessar o dashboard.

Utilize o menu lateral para navegar entre as ferramentas.

Dica: Sempre use * para multiplicações (ex: 2*s) e ** ou ^ para potências (ex: s**2).
