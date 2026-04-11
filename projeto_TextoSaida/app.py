import streamlit as st

# --- DOMÍNIO DE DADOS (RNF02 e RNF03) ---
# Dicionário para mapear as cores em português para CSS aplicável na web
CORES_PERMITIDAS = {
    'preto': 'black', 
    'branco': 'white', 
    'azul': 'blue', 
    'amarelo': '#D4AF37', # Usando um tom de amarelo mais escuro/mostarda para melhor leitura
    'cinza': 'gray'
}
COMPONENTES_PERMITIDOS = ['label', 'edit', 'memo']

# --- MODELO LÓGICO (Diagrama de Classes & RNF01) ---
class TextoSaida:
    def __init__(self):
        # Atributos definidos no diagrama de classes
        self.texto = ""
        self.tamanhoLetra = 12
        self.corFont = "preto"
        self.corFundo = "branco"
        self.tipoComp = "label"

    # Métodos definidos no diagrama
    def configurarTexto(self, texto: str) -> None:
        self.texto = texto

    def defTamanhoLetr(self, tamanho: int) -> None:
        if tamanho > 0:
            self.tamanhoLetra = tamanho
        else:
            raise ValueError("O tamanho da letra deve ser positivo.")

    def defCorFonte(self, cor: str) -> None:
        # RF06: Validação da paleta
        if cor.lower() in CORES_PERMITIDAS:
            self.corFont = cor.lower()
        else:
            raise ValueError(f"Cor de fonte inválida. Escolha entre: {', '.join(CORES_PERMITIDAS.keys())}")

    def defCorFundo(self, cor: str) -> None:
        # RF06: Validação da paleta
        if cor.lower() in CORES_PERMITIDAS:
            self.corFundo = cor.lower()
        else:
            raise ValueError(f"Cor de fundo inválida. Escolha entre: {', '.join(CORES_PERMITIDAS.keys())}")

    def defTipoComponent(self, tipoComp: str) -> None:
        if tipoComp.lower() in COMPONENTES_PERMITIDOS:
            self.tipoComp = tipoComp.lower()
        else:
            raise ValueError(f"Componente inválido. Escolha entre: {', '.join(COMPONENTES_PERMITIDOS)}")

    def exibir(self) -> dict:
        # Para manter a independência (RNF01), o método exibir entrega as propriedades 
        # para que qualquer plataforma (Web, Desktop, Mobile) decida como renderizar.
        return {
            "texto": self.texto,
            "tamanhoLetra": self.tamanhoLetra,
            "corFont": self.corFont,
            "corFundo": self.corFundo,
            "tipoComp": self.tipoComp
        }


# --- INTERFACE VISUAL COM STREAMLIT ---
st.set_page_config(page_title="Exercício: TextoSaída", layout="centered")

st.title("🧩 Construtor de Componentes")
st.markdown("Implementação da classe `TextoSaída` com independência de plataforma.")
st.divider()

# Formulário de entrada (Atendendo RF01 a RF05)
with st.form("form_configuracao"):
    st.subheader("Configurações do Componente")
    
    input_texto = st.text_input("Texto (RF01):", value="Olá, mundo!")
    input_tamanho = st.number_input("Tamanho da Fonte (RF02):", min_value=8, max_value=72, value=16)
    
    col1, col2 = st.columns(2)
    with col1:
        input_cor_fonte = st.selectbox("Cor da Fonte (RF03):", list(CORES_PERMITIDAS.keys()), index=0)
    with col2:
        input_cor_fundo = st.selectbox("Cor do Fundo (RF04):", list(CORES_PERMITIDAS.keys()), index=1)
        
    input_tipo = st.radio("Componente de Destino (RF05):", COMPONENTES_PERMITIDOS, horizontal=True)
    
    btn_gerar = st.form_submit_button("Construir e Exibir")

# Lógica de processamento e renderização
if btn_gerar:
    try:
        # Instanciando a classe e usando estritamente os métodos do diagrama
        componente = TextoSaida()
        componente.configurarTexto(input_texto)
        componente.defTamanhoLetr(int(input_tamanho))
        componente.defCorFonte(input_cor_fonte)
        componente.defCorFundo(input_cor_fundo)
        componente.defTipoComponent(input_tipo)
        
        # Recuperando as configs pelo método exibir()
        config = componente.exibir()
        
        st.divider()
        st.subheader("Resultado Renderizado:")
        
        # Traduzindo as cores conceituais para CSS real
        css_fonte = CORES_PERMITIDAS[config["corFont"]]
        css_fundo = CORES_PERMITIDAS[config["corFundo"]]
        tamanho = config["tamanhoLetra"]
        texto = config["texto"]
        
        # Estilo base CSS compartilhado
        style = f"color: {css_fonte}; background-color: {css_fundo}; font-size: {tamanho}px; padding: 10px; border-radius: 5px; width: 100%; border: 1px solid #ccc; font-family: sans-serif;"
        
        # Simulando os componentes visuais solicitados (Label, Edit, Memo) usando HTML/CSS
        if config["tipoComp"] == "label":
            html_saida = f'<div style="{style}">{texto}</div>'
            
        elif config["tipoComp"] == "edit":
            html_saida = f'<input type="text" value="{texto}" style="{style}" readonly>'
            
        elif config["tipoComp"] == "memo":
            html_saida = f'<textarea style="{style} min-height: 120px;" readonly>{texto}</textarea>'
            
        # Exibindo o componente criado de forma segura no Streamlit
        st.markdown(html_saida, unsafe_allow_html=True)
        
    except ValueError as e:
        # Captura as validações do RF06
        st.error(f"Erro de Validação: {e}")