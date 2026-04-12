# 💡 PROJETO – Gestão de Conta de Luz

> Projeto de Engenharia de Software · Python + Streamlit

---

## 📐 1. Diagrama de Classes

O diagrama acima descreve a estrutura do sistema, utilizando a classe TextoSaída para representar e formatar a exibição de informações textuais, permitindo o controle de atributos como tamanho da letra, cores e tipo de componente.

![Diagrama de Classes](./assets/UML_TextoSaida.png)

---

## ✅ 2. Requisitos Funcionais (RF)

- RF01: O sistema deve permitir a inserção de um conteúdo de texto.
- RF02: O sistema deve permitir a configuração do tamanho da fonte.
- RF03: O sistema deve permitir a escolha da cor da fonte entre cinco opções (preto, branco, azul, amarelo, cinza).
- RF04: O sistema deve permitir a escolha da cor de fundo entre cinco opções (preto, branco, azul, amarelo, cinza).
- RF05: O sistema deve permitir ao usuário selecionar o componente de destino (Label, Edit ou Memo).
- RF06: O sistema deve validar se as cores escolhidas estão dentro da paleta permitida.
---

## 🔒 3. Requisitos Não Funcionais (NRF)

- RNF01 (Independência de Plataforma): A classe não deve herdar de classes visuais específicas de frameworks, deve manter o foco conceitual
- RNF02 (Restrição de Domínio): As cores devem ser limitadas estritamente aos tons: preto, branco, azul, amarelo e cinza.
- RNF03 (Usabilidade): Os componentes de exibição permitidos devem ser restritos exclusivamente a label, edit e memo
- RNF04 (Extensibilidade): A estrutura deve permitir que novos tipos de componentes sejam adicionados futuramente sem quebrar a lógica de atributos.
---

## 🧠 4. Engenharia de Prompt

### Prompt utilizado

```
Baseado nos requisitos funcionais e não funcionais e no diagrama de classes em anexo,
construa uma aplicação com Python e Streamlit em um único arquivo com funcionalidades
necessárias e aplicações para funcionar agora mesmo.
```

### Análise das técnicas aplicadas

| Técnica | Como foi aplicada |
|---|---|
| **Contexto rico** | Diagrama UML + RFs + NRFs fornecidos como contexto estruturado junto ao prompt |
| **Restrição de stack** | `"Python e Streamlit em um único arquivo"` – delimita tecnologias e formato de entrega |
| **Orientação ao resultado** | `"funcionar agora mesmo"` – evita saídas parciais ou apenas explicativas |
| **Completude implícita** | `"funcionalidades necessárias"` – o modelo infere o que não foi listado explicitamente |
| **Multimodal** | Imagem do diagrama de classes enviada junto ao prompt textual |

---

## 🖥️ 5. Projeto em Execução

O sistema apresenta uma interface web onde o usuário configura propriedades textuais via formulário. Ao submeter os dados, a aplicação valida as informações através da classe TextoSaída e renderiza instantaneamente na tela o componente escolhido (Label, Edit ou Memo) com as exatas formatações de cor e tamanho aplicadas.

![Projeto rodando](./assets\LayoutTextoSaída.png)

---

## 🚀 6. Como Fazer o Projeto Rodar

### Pré-requisito

- **Python 3.8+** → Baixe em [https://www.python.org/downloads/](https://www.python.org/downloads/)

---

### Passo 1 – Salve o arquivo

Salve o arquivo `app.py` em uma pasta de sua preferência:

```
# Windows
C:\Projetos\boneco\app.py

# Mac / Linux
~/projetos/boneco/app.py
```

---

### Passo 2 – Instale o Streamlit

Abra o terminal (Prompt de Comando no Windows / Terminal no Mac-Linux) e execute:

```bash
pip install streamlit pandas
```

---

### Passo 3 – Execute a aplicação

No terminal, navegue até a pasta do arquivo e execute:

```bash
# Windows
cd C:\Projetos\boneco

# Mac / Linux
cd ~/projetos/boneco

# Rodar
streamlit run boneco_app.py
```

---

### Passo 4 – Acesse no navegador

O Streamlit abrirá o navegador automaticamente. Se não abrir, acesse manualmente:

```
http://localhost:8501
```

---

### Passo 5 – Use a aplicação

| Passo | O que fazer |
|---|---|
| **1º passo** | Preencha as configurações do componente (Texto, Tamanho, Cores e Tipo) no formulário |
| **2º passo** | Clique no botão **Construir e Exibir** para gerar o componente na tela |
| 🧩 *(extra)* | Visualize o **Resultado Renderizado** refletindo exatamente as suas escolhas |
| 🔄 *(extra)* | Alterne entre **Label, Edit ou Memo** para ver as diferentes representações visuais |

*Projeto gerado com Engenharia de Prompt · Python 3 · Streamlit · 2026*