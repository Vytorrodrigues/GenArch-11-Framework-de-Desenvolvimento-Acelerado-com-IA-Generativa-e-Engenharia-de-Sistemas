"""
TextoSaida — Aplicação Streamlit
Baseado no diagrama de classes UML e requisitos funcionais/não funcionais.
"""

import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# CLASSE TextoSaida (RF01–RF06 / RNF01–RNF04)
# ──────────────────────────────────────────────────────────────────────────────

CORES_PERMITIDAS = {"preto", "branco", "azul", "amarelo", "cinza"}   # RNF02
COMPONENTES_PERMITIDOS = {"label", "edit", "memo"}                    # RNF03


class TextoSaida:
    """
    Classe conceitual (RNF01 – sem herança de frameworks visuais).
    Encapsula texto, estilo tipográfico e componente de destino.
    """

    def __init__(self):
        self.texto: str = ""
        self.tamanhoLetra: int = 16
        self.corFont: str = "preto"
        self.corFundo: str = "branco"
        self.tipoComp: str = "label"

    # ── setters ──────────────────────────────────────────────────────────────

    def configurarTexto(self, texto: str) -> None:              # RF01
        self.texto = texto

    def defTamanhoLetr(self, tamanho: int) -> None:             # RF02
        if tamanho < 8:
            tamanho = 8
        if tamanho > 72:
            tamanho = 72
        self.tamanhoLetra = tamanho

    def defCorFonte(self, cor: str) -> None:                    # RF03 / RF06
        cor = cor.lower().strip()
        if cor not in CORES_PERMITIDAS:
            raise ValueError(f"Cor '{cor}' não permitida. Use: {CORES_PERMITIDAS}")
        self.corFont = cor

    def defCorFundo(self, cor: str) -> None:                    # RF04 / RF06
        cor = cor.lower().strip()
        if cor not in CORES_PERMITIDAS:
            raise ValueError(f"Cor '{cor}' não permitida. Use: {CORES_PERMITIDAS}")
        self.corFundo = cor

    def defTipoComponent(self, tipoComp: str) -> None:          # RF05
        tipoComp = tipoComp.lower().strip()
        if tipoComp not in COMPONENTES_PERMITIDOS:
            raise ValueError(f"Componente '{tipoComp}' não permitido. Use: {COMPONENTES_PERMITIDOS}")
        self.tipoComp = tipoComp

    # ── exibir ───────────────────────────────────────────────────────────────

    def exibir(self) -> dict:
        """Retorna os atributos para renderização visual."""
        return {
            "texto": self.texto,
            "tamanhoLetra": self.tamanhoLetra,
            "corFont": self.corFont,
            "corFundo": self.corFundo,
            "tipoComp": self.tipoComp,
        }


# ──────────────────────────────────────────────────────────────────────────────
# MAPEAMENTOS DE COR (hex)
# ──────────────────────────────────────────────────────────────────────────────

COR_HEX = {
    "preto":   "#111111",
    "branco":  "#F5F5F5",
    "azul":    "#1A73E8",
    "amarelo": "#F9AB00",
    "cinza":   "#9AA0A6",
}

COR_LABEL = {
    "preto":   "Preto ⬛",
    "branco":  "Branco ⬜",
    "azul":    "Azul 🟦",
    "amarelo": "Amarelo 🟨",
    "cinza":   "Cinza 🩶",
}


def hex_legivel(fundo_hex: str, fonte_hex: str) -> str:
    """Retorna a cor de texto com melhor contraste (simples)."""
    return fonte_hex


# ──────────────────────────────────────────────────────────────────────────────
# INTERFACE STREAMLIT
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="TextoSaida",
    page_icon="🖋️",
    layout="centered",
)

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    letter-spacing: -0.03em;
}

.titulo-app {
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.04em;
    margin-bottom: 0;
}

.subtitulo-app {
    font-size: 0.85rem;
    color: #888;
    font-family: 'DM Mono', monospace;
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
}

.secao {
    background: #FAFAFA;
    border: 1px solid #E8E8E8;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.secao-titulo {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #999;
    margin-bottom: 0.8rem;
    font-family: 'DM Mono', monospace;
}

/* Preview box */
.preview-wrapper {
    border: 2px dashed #D0D0D0;
    border-radius: 14px;
    padding: 0.5rem;
    background: #F0F0F0;
    margin-top: 1rem;
}

.preview-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #AAA;
    font-family: 'DM Mono', monospace;
    text-align: center;
    margin-bottom: 0.4rem;
}

.badge-comp {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    background: #ffffff;
    color: #fff;
    border-radius: 6px;
    padding: 2px 8px;
    margin-bottom: 0.6rem;
}

.status-ok  { color: #34A853; font-weight: 600; }
.status-err { color: #EA4335; font-weight: 600; }

div[data-testid="stHorizontalBlock"] > div { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown('<div class="titulo-app">🖋️ TextoSaida</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-app">Configurador de componente de texto · Python + Streamlit</div>', unsafe_allow_html=True)

# ── Estado da sessão ──────────────────────────────────────────────────────────
if "obj" not in st.session_state:
    st.session_state.obj = TextoSaida()
    st.session_state.erros = []

obj: TextoSaida = st.session_state.obj

# ──────────────────────────────────────────────────────────────────────────────
# PAINEL DE CONFIGURAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

col_cfg, col_prev = st.columns([1.15, 1], gap="large")

with col_cfg:

    # RF01 – Texto
    st.markdown('<div class="secao-titulo">📝 Conteúdo (RF01)</div>', unsafe_allow_html=True)
    texto_input = st.text_area(
        "Texto de saída",
        value=obj.texto,
        height=100,
        placeholder="Digite o conteúdo a exibir…",
        label_visibility="collapsed",
    )

    st.divider()

    # RF02 – Tamanho da fonte
    st.markdown('<div class="secao-titulo">🔡 Tamanho da fonte (RF02)</div>', unsafe_allow_html=True)
    tamanho_input = st.slider("Tamanho (px)", min_value=8, max_value=72,
                               value=obj.tamanhoLetra, step=1,
                               label_visibility="collapsed")

    st.divider()

    # RF03 / RF04 – Cores
    st.markdown('<div class="secao-titulo">🎨 Cores (RF03 · RF04 · RF06 · RNF02)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        cor_fonte_input = st.selectbox(
            "Cor da fonte",
            options=list(CORES_PERMITIDAS),
            index=list(CORES_PERMITIDAS).index(obj.corFont),
            format_func=lambda c: COR_LABEL[c],
        )
    with c2:
        cor_fundo_input = st.selectbox(
            "Cor do fundo",
            options=list(CORES_PERMITIDAS),
            index=list(CORES_PERMITIDAS).index(obj.corFundo),
            format_func=lambda c: COR_LABEL[c],
        )

    st.divider()

    # RF05 – Componente
    st.markdown('<div class="secao-titulo">🧩 Componente de destino (RF05 · RNF03)</div>', unsafe_allow_html=True)
    comp_input = st.radio(
        "Tipo de componente",
        options=list(COMPONENTES_PERMITIDOS),
        index=list(COMPONENTES_PERMITIDOS).index(obj.tipoComp),
        horizontal=True,
        format_func=str.capitalize,
        label_visibility="collapsed",
    )

    st.divider()

    # Botão aplicar
    aplicar = st.button("✅  Aplicar configurações", use_container_width=True, type="primary")

# ──────────────────────────────────────────────────────────────────────────────
# LÓGICA DE APLICAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

erros: list[str] = []

if aplicar:
    try:
        obj.configurarTexto(texto_input)
        obj.defTamanhoLetr(tamanho_input)
        obj.defCorFonte(cor_fonte_input)
        obj.defCorFundo(cor_fundo_input)
        obj.defTipoComponent(comp_input)
        st.session_state.erros = []
    except ValueError as e:
        st.session_state.erros = [str(e)]
else:
    # Sincroniza sem validar (para o preview em tempo real)
    obj.texto = texto_input
    obj.tamanhoLetra = tamanho_input
    obj.corFont = cor_fonte_input
    obj.corFundo = cor_fundo_input
    obj.tipoComp = comp_input

dados = obj.exibir()

# ──────────────────────────────────────────────────────────────────────────────
# PREVIEW
# ──────────────────────────────────────────────────────────────────────────────

with col_prev:
    st.markdown("#### Pré-visualização")

    fundo_hex = COR_HEX[dados["corFundo"]]
    fonte_hex = COR_HEX[dados["corFont"]]
    tamanho   = dados["tamanhoLetra"]
    comp      = dados["tipoComp"]
    txt       = dados["texto"] or "⬡ Nenhum texto inserido…"

    # Estilo por componente
    border_radius = {"label": "8px", "edit": "6px", "memo": "10px"}[comp]
    border_style  = {
        "label": f"2px solid {fonte_hex}33",
        "edit":  f"2px solid {fonte_hex}88",
        "memo":  f"2px dashed {fonte_hex}66",
    }[comp]
    min_height = {"label": "60px", "edit": "60px", "memo": "140px"}[comp]
    align      = {"label": "center", "edit": "left", "memo": "left"}[comp]
    padding    = {"label": "18px 24px", "edit": "10px 14px", "memo": "14px 18px"}[comp]
    cursor     = {"label": "default", "edit": "text", "memo": "text"}[comp]

    # Simula barra de cursor para Edit
    caret = '<span style="border-right:2px solid currentColor;animation:blink 1s step-end infinite"> </span>' if comp == "edit" else ""
    anim_css = "<style>@keyframes blink{50%{opacity:0}}</style>" if comp == "edit" else ""

    preview_html = f"""
    {anim_css}
    <div style="
        background:{fundo_hex};
        color:{fonte_hex};
        font-size:{tamanho}px;
        border-radius:{border_radius};
        border:{border_style};
        min-height:{min_height};
        padding:{padding};
        text-align:{align};
        cursor:{cursor};
        display:flex;
        align-items:{'center' if comp=='label' else 'flex-start'};
        word-break:break-word;
        white-space:pre-wrap;
        font-family:{'DM Sans, sans-serif' if comp!='edit' else 'DM Mono, monospace'};
        box-shadow: 0 4px 24px {fundo_hex}55;
        transition: all 0.3s ease;
    ">
        {txt}{caret}
    </div>
    """

    st.markdown('<div class="preview-label">PREVIEW</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="badge-comp">{comp.upper()}</div>', unsafe_allow_html=True)
    st.markdown(preview_html, unsafe_allow_html=True)

    # Erros de validação (RF06)
    if st.session_state.erros:
        for e in st.session_state.erros:
            st.error(f"⚠️ {e}")
    elif aplicar:
        st.success("✅ Configurações aplicadas com sucesso!")

# ──────────────────────────────────────────────────────────────────────────────
# ESTADO DO OBJETO (debug / transparência)
# ──────────────────────────────────────────────────────────────────────────────

with st.expander("🔍 Estado atual do objeto `TextoSaida`", expanded=False):
    st.markdown('<div class="secao-titulo">Atributos (via exibir())</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("tamanhoLetra", f"{dados['tamanhoLetra']} px")
    c2.metric("corFont", dados["corFont"].capitalize())
    c3.metric("corFundo", dados["corFundo"].capitalize())

    st.code(f"""
texto      = "{dados['texto']}"
tamanhoLetra = {dados['tamanhoLetra']}
corFont    = "{dados['corFont']}"
corFundo   = "{dados['corFundo']}"
tipoComp   = "{dados['tipoComp']}"
    """, language="python")

# ──────────────────────────────────────────────────────────────────────────────
# RODAPÉ
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<span style="font-family:DM Mono,monospace;font-size:0.7rem;color:#BBB;">'
    'TextoSaida · RF01–RF06 · RNF01–RNF04 · Python + Streamlit'
    '</span>',
    unsafe_allow_html=True,
)