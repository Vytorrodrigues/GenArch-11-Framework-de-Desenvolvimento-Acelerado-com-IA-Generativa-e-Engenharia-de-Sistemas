import streamlit as st
import time

# ─────────────────────────────────────────
#  Enumeração Direção (RF03 / NRF03)
# ─────────────────────────────────────────
class Direcao:
    CIMA      = "⬆️ Cima"
    BAIXO     = "⬇️ Baixo"
    ESQUERDA  = "⬅️ Esquerda"
    DIREITA   = "➡️ Direita"


# ─────────────────────────────────────────
#  Classe Boneco (fiel ao diagrama de classes)
# ─────────────────────────────────────────
class Boneco:
    def __init__(self, nome: str):
        self.nome: str      = nome          # RF01
        self.posicaoX: int  = 5             # RF02 – posição inicial centro
        self.posicaoY: int  = 5
        self.direcao: str   = Direcao.CIMA  # RF03

    # RF02 / RF03
    def exibirPosicao(self) -> str:
        return f"X={self.posicaoX}, Y={self.posicaoY}"

    # RF04 / RF08
    def moverParaCima(self):
        self.posicaoY = max(0, self.posicaoY - 1)
        self.direcao  = Direcao.CIMA

    # RF05 / RF08
    def moverParaBaixo(self):
        self.posicaoY = min(10, self.posicaoY + 1)
        self.direcao  = Direcao.BAIXO

    # RF06 / RF08
    def moverParaEsquerda(self):
        self.posicaoX = max(0, self.posicaoX - 1)
        self.direcao  = Direcao.ESQUERDA

    # RF07 / RF08
    def moverParaDireita(self):
        self.posicaoX = min(10, self.posicaoX + 1)
        self.direcao  = Direcao.DIREITA


# ─────────────────────────────────────────
#  Configuração da página
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Boneco – Simulador",
    page_icon="🕹️",
    layout="centered",
)

# ─────────────────────────────────────────
#  CSS customizado  (NRF04 – interface limpa)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Mono', monospace;
    background: #0a0a0f;
    color: #e8e8f0;
}

.main { background: #0a0a0f; }

h1, h2, h3 {
    font-family: 'Syne', sans-serif;
    letter-spacing: -1px;
}

/* Grid do mundo */
.grid-world {
    display: grid;
    grid-template-columns: repeat(11, 1fr);
    gap: 3px;
    background: #12121a;
    border: 2px solid #2a2a3a;
    border-radius: 12px;
    padding: 10px;
    width: 100%;
    aspect-ratio: 1;
    max-width: 420px;
    margin: 0 auto;
}

.cell {
    aspect-ratio: 1;
    background: #1a1a28;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    transition: background 0.15s;
}

.cell.active {
    background: #2d1f6e;
    box-shadow: 0 0 12px #7c3aed88;
    animation: pulse 0.5s ease-out;
}

@keyframes pulse {
    0%   { transform: scale(1.35); }
    100% { transform: scale(1); }
}

/* Cartão de status */
.status-card {
    background: #12121a;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    font-size: 0.9rem;
    line-height: 1.8;
}

.status-card .label { color: #6b6b8a; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; }
.status-card .value { color: #a78bfa; font-weight: 700; font-size: 1.05rem; }

/* Botões de movimento */
.stButton > button {
    width: 100%;
    background: #1e1e2e !important;
    color: #e8e8f0 !important;
    border: 1px solid #3a3a5a !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.4rem !important;
    padding: 10px !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    background: #2d1f6e !important;
    border-color: #7c3aed !important;
    box-shadow: 0 0 16px #7c3aed55 !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: scale(0.96) !important;
}

/* Input */
.stTextInput > div > div > input {
    background: #12121a !important;
    color: #e8e8f0 !important;
    border: 1px solid #3a3a5a !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
}

/* Título principal */
.hero-title {
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}

.hero-sub {
    text-align: center;
    color: #4a4a6a;
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 24px;
}

/* Rastro */
.trail-cell {
    background: #1e1a3a !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  Estado da sessão  (persiste entre cliques)
# ─────────────────────────────────────────
if "boneco" not in st.session_state:
    st.session_state.boneco    = None
    st.session_state.cadastrado = False
    st.session_state.trail     = set()   # NRF05 – rastro visual

boneco: Boneco = st.session_state.boneco


# ─────────────────────────────────────────
#  TELA 1 – Cadastro (RF01)  ← 1º clique
# ─────────────────────────────────────────
st.markdown('<div class="hero-title">🕹️ BONECO</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Simulador de Movimento</div>', unsafe_allow_html=True)

if not st.session_state.cadastrado:
    st.markdown("#### Cadastrar Boneco")
    nome_input = st.text_input("Nome do boneco", placeholder="Ex.: Pixel", label_visibility="collapsed")

    if st.button("▶  Iniciar", use_container_width=True):
        if nome_input.strip():
            st.session_state.boneco     = Boneco(nome_input.strip())
            st.session_state.cadastrado = True
            st.session_state.trail      = {(5, 5)}
            st.rerun()
        else:
            st.warning("Digite um nome para o boneco.")
    st.stop()


# ─────────────────────────────────────────
#  TELA 2 – Jogo  (RF02-RF08)  ← 2º clique
# ─────────────────────────────────────────
boneco = st.session_state.boneco
trail  = st.session_state.trail

# ── Status (RF02 / RF03) ──────────────────
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    st.markdown(f"""
    <div class="status-card">
        <div class="label">Boneco</div>
        <div class="value">{boneco.nome}</div>
    </div>""", unsafe_allow_html=True)

with col_s2:
    st.markdown(f"""
    <div class="status-card">
        <div class="label">Posição</div>
        <div class="value">{boneco.exibirPosicao()}</div>
    </div>""", unsafe_allow_html=True)

with col_s3:
    st.markdown(f"""
    <div class="status-card">
        <div class="label">Direção</div>
        <div class="value">{boneco.direcao}</div>
    </div>""", unsafe_allow_html=True)


# ── Grid / Mundo (NRF05 – boneco se move na tela) ──
GRID = 11
BONECO_EMOJI = "😀"
TRAIL_EMOJI  = "·"

cells_html = ""
for row in range(GRID):
    for col in range(GRID):
        is_boneco = (col == boneco.posicaoX and row == boneco.posicaoY)
        is_trail  = (col, row) in trail and not is_boneco

        if is_boneco:
            cells_html += f'<div class="cell active">{BONECO_EMOJI}</div>'
        elif is_trail:
            cells_html += f'<div class="cell trail-cell"><span style="color:#3a3a5a;font-size:.7rem">{TRAIL_EMOJI}</span></div>'
        else:
            cells_html += '<div class="cell"></div>'

st.markdown(f'<div class="grid-world">{cells_html}</div>', unsafe_allow_html=True)

st.write("")  # espaço

# ── D-pad (NRF04 – 2 cliques: cadastrar + mover) ──
_, col_up, _ = st.columns([1, 1, 1])
col_left, col_center, col_right = st.columns([1, 1, 1])
_, col_down, _ = st.columns([1, 1, 1])

with col_up:
    if st.button("⬆️", use_container_width=True, key="up"):
        boneco.moverParaCima()
        trail.add((boneco.posicaoX, boneco.posicaoY))
        st.rerun()

with col_left:
    if st.button("⬅️", use_container_width=True, key="left"):
        boneco.moverParaEsquerda()
        trail.add((boneco.posicaoX, boneco.posicaoY))
        st.rerun()

with col_center:
    # Botão resetar posição
    if st.button("🏠", use_container_width=True, key="reset"):
        boneco.posicaoX = 5
        boneco.posicaoY = 5
        boneco.direcao  = Direcao.CIMA
        st.session_state.trail = {(5, 5)}
        st.rerun()

with col_right:
    if st.button("➡️", use_container_width=True, key="right"):
        boneco.moverParaDireita()
        trail.add((boneco.posicaoX, boneco.posicaoY))
        st.rerun()

with col_down:
    if st.button("⬇️", use_container_width=True, key="down"):
        boneco.moverParaBaixo()
        trail.add((boneco.posicaoX, boneco.posicaoY))
        st.rerun()

st.write("")

# ── Botão trocar boneco ──
if st.button("🔄  Trocar boneco", use_container_width=False):
    st.session_state.boneco     = None
    st.session_state.cadastrado = False
    st.session_state.trail      = set()
    st.rerun()

st.markdown(
    '<p style="text-align:center;color:#2a2a4a;font-size:.7rem;margin-top:24px;">🏠 = resetar posição · rastro mostra o caminho percorrido</p>',
    unsafe_allow_html=True
)