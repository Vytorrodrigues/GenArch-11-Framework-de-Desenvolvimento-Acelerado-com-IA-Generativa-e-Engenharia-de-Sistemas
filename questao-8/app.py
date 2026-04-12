"""
ColecaoCD - Gerenciador de Coleção de CDs
Arquivo único: app.py
Executar: streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ColecaoCD",
    page_icon="💿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM / CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --primary:   #E63946;
    --secondary: #457B9D;
    --bg:        #0D1117;
    --surface:   #161B22;
    --surface2:  #21262D;
    --border:    #30363D;
    --text:      #E6EDF3;
    --muted:     #8B949E;
    --success:   #3FB950;
    --error:     #F85149;
    --warning:   #D29922;
    --accent:    #58A6FF;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Radio sidebar */
div[data-testid="stRadio"] label {
    font-size: 0.95rem !important;
    padding: 0.4rem 0 !important;
}

/* Inputs */
input, textarea, select,
div[data-baseweb="select"] div,
div[data-baseweb="input"] input {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
}
div[data-baseweb="select"] {
    background-color: var(--surface2) !important;
    border-radius: 6px !important;
}

/* Buttons */
.stButton > button {
    background-color: var(--primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em;
    transition: opacity 0.15s;
}
.stButton > button:hover { opacity: 0.85; }

.btn-secondary > button {
    background-color: var(--secondary) !important;
}
.btn-danger > button {
    background-color: var(--error) !important;
}
.btn-success > button {
    background-color: var(--success) !important;
}
.btn-neutral > button {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
}

/* Cards */
.cd-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.cd-card:hover { border-color: var(--secondary); }

.cd-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 0.15rem 0;
}
.cd-artist {
    font-size: 0.9rem;
    color: var(--accent);
    font-family: 'Space Mono', monospace;
    margin: 0 0 0.1rem 0;
}
.cd-year {
    font-size: 0.8rem;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
}

/* Tags */
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    margin-right: 4px;
}
.tag-primary   { background: rgba(230,57,70,0.15);  color: var(--primary);   border: 1px solid var(--primary); }
.tag-secondary { background: rgba(69,123,157,0.15); color: var(--secondary); border: 1px solid var(--secondary); }

/* Alerts */
.alert {
    padding: 0.7rem 1rem;
    border-radius: 6px;
    font-size: 0.9rem;
    margin: 0.5rem 0;
    font-family: 'Space Mono', monospace;
}
.alert-success { background: rgba(63,185,80,0.12);  border: 1px solid var(--success); color: var(--success); }
.alert-error   { background: rgba(248,81,73,0.12);  border: 1px solid var(--error);   color: var(--error);   }
.alert-warning { background: rgba(210,153,34,0.12); border: 1px solid var(--warning); color: var(--warning); }
.alert-info    { background: rgba(88,166,255,0.12); border: 1px solid var(--accent);  color: var(--accent);  }

/* Page header */
.page-header {
    border-bottom: 2px solid var(--primary);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}
.page-header h1 {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
}
.page-header p {
    color: var(--muted);
    font-size: 0.85rem;
    margin: 0.2rem 0 0 0;
    font-family: 'Space Mono', monospace;
}

/* Stats */
.stat-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary);
    line-height: 1;
}
.stat-label {
    font-size: 0.78rem;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-top: 0.3rem;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Expander */
details summary {
    color: var(--accent) !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PERSISTÊNCIA JSON
# ─────────────────────────────────────────────
DATA_FILE = "colecao_data.json"

MOCK_DATA = {
    "artistas": [
        {"nome": "The Beatles"},
        {"nome": "Pink Floyd"},
        {"nome": "Led Zeppelin"},
        {"nome": "Nirvana"},
        {"nome": "Radiohead"},
        {"nome": "Metallica"},
    ],
    "cds": [
        {"titulo": "Abbey Road",              "anoLancamento": 1969, "artista": "The Beatles"},
        {"titulo": "Sgt. Pepper's",           "anoLancamento": 1967, "artista": "The Beatles"},
        {"titulo": "The Dark Side of the Moon","anoLancamento": 1973, "artista": "Pink Floyd"},
        {"titulo": "Wish You Were Here",      "anoLancamento": 1975, "artista": "Pink Floyd"},
        {"titulo": "Led Zeppelin IV",         "anoLancamento": 1971, "artista": "Led Zeppelin"},
        {"titulo": "Nevermind",               "anoLancamento": 1991, "artista": "Nirvana"},
        {"titulo": "In Utero",                "anoLancamento": 1993, "artista": "Nirvana"},
        {"titulo": "OK Computer",             "anoLancamento": 1997, "artista": "Radiohead"},
        {"titulo": "Master of Puppets",       "anoLancamento": 1986, "artista": "Metallica"},
    ],
}


def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    save_data(MOCK_DATA)
    return MOCK_DATA.copy()


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# ENTIDADES (classes do diagrama)
# ─────────────────────────────────────────────
class Artista:
    def __init__(self, nome: str):
        self.nome = nome

    def get_nome(self) -> str:
        return self.nome

    def to_dict(self) -> dict:
        return {"nome": self.nome}

    @staticmethod
    def from_dict(d: dict) -> "Artista":
        return Artista(d["nome"])


class Cd:
    def __init__(self, titulo: str, ano: int, artista: str):
        self._titulo = titulo
        self._anoLancamento = ano
        self._artista = artista  # derived — nome do artista

    def get_titulo(self) -> str:
        return self._titulo

    def get_ano_lancamento(self) -> int:
        return self._anoLancamento

    def get_artista(self) -> str:
        return self._artista

    def editar_cd(self, novo_titulo: str, novo_ano: int, novo_artista: str) -> None:
        self._titulo = novo_titulo
        self._anoLancamento = novo_ano
        self._artista = novo_artista

    def to_dict(self) -> dict:
        return {
            "titulo": self._titulo,
            "anoLancamento": self._anoLancamento,
            "artista": self._artista,
        }

    @staticmethod
    def from_dict(d: dict) -> "Cd":
        return Cd(d["titulo"], d["anoLancamento"], d["artista"])


class ColecaoCD:
    def __init__(self, list_cds: list[Cd]):
        self._list_cds: list[Cd] = list_cds

    def cadastrar_cd(self, nome_artista: str, titulo: str, ano: int) -> tuple[bool, str]:
        # RF08 — evitar duplicidade
        for cd in self._list_cds:
            if (cd.get_artista().lower() == nome_artista.lower()
                    and cd.get_titulo().lower() == titulo.lower()
                    and cd.get_ano_lancamento() == ano):
                return False, "CD já cadastrado com mesmo artista, título e ano."
        novo = Cd(titulo, ano, nome_artista)
        self._list_cds.append(novo)
        return True, "CD cadastrado com sucesso!"

    def listar_todos(self) -> list[Cd]:
        return list(self._list_cds)

    def pesquisar_por_artista(self, nome_artista: str) -> list[Cd]:
        term = nome_artista.lower()
        return [cd for cd in self._list_cds if term in cd.get_artista().lower()]

    def pesquisar_por_titulo(self, termo_parcial: str) -> list[Cd]:
        term = termo_parcial.lower()
        return [cd for cd in self._list_cds if term in cd.get_titulo().lower()]

    def excluir_cd(self, cd: Cd) -> bool:
        if cd in self._list_cds:
            self._list_cds.remove(cd)
            return True
        return False

    def get_cd_by_index(self, idx: int) -> Cd | None:
        if 0 <= idx < len(self._list_cds):
            return self._list_cds[idx]
        return None

    def to_list(self) -> list[dict]:
        return [cd.to_dict() for cd in self._list_cds]


# ─────────────────────────────────────────────
# HELPERS / STATE
# ─────────────────────────────────────────────
def get_state():
    if "data" not in st.session_state:
        raw = load_data()
        st.session_state.data = raw
    if "flash" not in st.session_state:
        st.session_state.flash = None
    return st.session_state.data


def persist():
    save_data(st.session_state.data)


def set_flash(msg: str, kind: str = "success"):
    st.session_state.flash = {"msg": msg, "kind": kind}


def show_flash():
    if st.session_state.get("flash"):
        f = st.session_state.flash
        st.markdown(f'<div class="alert alert-{f["kind"]}">{f["msg"]}</div>',
                    unsafe_allow_html=True)
        st.session_state.flash = None


def build_colecao(data: dict) -> ColecaoCD:
    cds = [Cd.from_dict(d) for d in data.get("cds", [])]
    return ColecaoCD(cds)


def build_artistas(data: dict) -> list[Artista]:
    return [Artista.from_dict(a) for a in data.get("artistas", [])]


def artista_names(data: dict) -> list[str]:
    return [a["nome"] for a in data.get("artistas", [])]


def validate_ano(ano: int) -> tuple[bool, str]:
    if not (1900 <= ano <= 2100):
        return False, "Ano deve estar entre 1900 e 2100."
    return True, ""


def html(content: str):
    st.markdown(content, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    html("""
    <div style="padding:1rem 0 1.5rem">
        <div style="font-size:2rem;text-align:center">💿</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                    text-align:center;letter-spacing:-0.02em;color:#E6EDF3">
            ColecaoCD
        </div>
        <div style="font-family:'Space Mono',monospace;font-size:0.7rem;
                    text-align:center;color:#8B949E;margin-top:2px">
            gerenciador de coleção
        </div>
    </div>
    """)

    st.markdown("---")
    page = st.radio(
        "Navegação",
        ["🏠  Dashboard",
         "🎤  Artistas",
         "💿  CDs",
         "🔍  Pesquisar",
         "✏️  Editar / Excluir"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    data = get_state()
    total_cds = len(data.get("cds", []))
    total_art = len(data.get("artistas", []))
    html(f"""
    <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#8B949E;
                padding:0 0.2rem">
        <div>💿 {total_cds} CDs cadastrados</div>
        <div style="margin-top:4px">🎤 {total_art} artistas</div>
    </div>
    """)

# ─────────────────────────────────────────────
# PÁGINAS
# ─────────────────────────────────────────────
data = get_state()

# ── DASHBOARD ──────────────────────────────
if page == "🏠  Dashboard":
    html("""
    <div class="page-header">
        <h1>Dashboard</h1>
        <p>visão geral da sua coleção</p>
    </div>
    """)
    show_flash()

    colecao = build_colecao(data)
    todos = colecao.listar_todos()
    artistas = build_artistas(data)

    anos = [cd.get_ano_lancamento() for cd in todos] if todos else [0]
    artistas_uniq = len(set(cd.get_artista() for cd in todos))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        html(f'<div class="stat-box"><div class="stat-number">{len(todos)}</div>'
             f'<div class="stat-label">Total de CDs</div></div>')
    with c2:
        html(f'<div class="stat-box"><div class="stat-number">{len(artistas)}</div>'
             f'<div class="stat-label">Artistas</div></div>')
    with c3:
        html(f'<div class="stat-box"><div class="stat-number">{min(anos) if todos else "—"}</div>'
             f'<div class="stat-label">CD mais antigo</div></div>')
    with c4:
        html(f'<div class="stat-box"><div class="stat-number">{max(anos) if todos else "—"}</div>'
             f'<div class="stat-label">CD mais recente</div></div>')

    st.markdown("---")

    if todos:
        html('<div style="font-size:1rem;font-weight:700;margin-bottom:0.8rem">🕐 Últimos CDs adicionados</div>')
        for cd in reversed(todos[-5:]):
            html(f"""
            <div class="cd-card">
                <div class="cd-title">💿 {cd.get_titulo()}</div>
                <div class="cd-artist">🎤 {cd.get_artista()}</div>
                <div class="cd-year">📅 {cd.get_ano_lancamento()}</div>
            </div>
            """)
    else:
        html('<div class="alert alert-info">Nenhum CD cadastrado ainda. Acesse a seção CDs para começar.</div>')


# ── ARTISTAS ───────────────────────────────
elif page == "🎤  Artistas":
    html("""
    <div class="page-header">
        <h1>Artistas</h1>
        <p>cadastro e listagem de artistas</p>
    </div>
    """)
    show_flash()

    artistas = build_artistas(data)
    nomes = artista_names(data)

    # Cadastrar
    with st.expander("➕ Cadastrar novo artista", expanded=True):
        with st.form("form_artista"):
            nome_input = st.text_input("Nome do artista / conjunto *")
            submitted = st.form_submit_button("Cadastrar Artista")
            if submitted:
                nome_input = nome_input.strip()
                if not nome_input:
                    html('<div class="alert alert-error">Nome é obrigatório.</div>')
                elif nome_input.lower() in [n.lower() for n in nomes]:
                    html('<div class="alert alert-warning">Artista já cadastrado.</div>')
                else:
                    novo = Artista(nome_input)
                    data["artistas"].append(novo.to_dict())
                    persist()
                    set_flash(f'Artista "{nome_input}" cadastrado com sucesso!')
                    st.rerun()

    st.markdown("---")
    html('<div style="font-size:1rem;font-weight:700;margin-bottom:0.8rem">'
         f'🎤 {len(artistas)} artista(s) cadastrado(s)</div>')

    if not artistas:
        html('<div class="alert alert-info">Nenhum artista cadastrado ainda.</div>')
    else:
        # Busca rápida
        busca = st.text_input("🔍 Filtrar artistas", placeholder="Digite parte do nome...")
        lista = [a for a in artistas
                 if busca.lower() in a.get_nome().lower()] if busca else artistas

        # Quantos CDs por artista
        cd_count = {}
        for cd in data.get("cds", []):
            cd_count[cd["artista"]] = cd_count.get(cd["artista"], 0) + 1

        for i, art in enumerate(lista):
            col_a, col_b, col_c = st.columns([5, 2, 1])
            with col_a:
                html(f'<div style="padding:0.5rem 0;font-weight:600">{art.get_nome()}</div>')
            with col_b:
                n = cd_count.get(art.get_nome(), 0)
                html(f'<div style="padding:0.5rem 0;color:#8B949E;font-family:\'Space Mono\',monospace;'
                     f'font-size:0.8rem">{n} CD(s)</div>')
            with col_c:
                if st.button("🗑️", key=f"del_art_{i}",
                             help="Excluir artista",
                             disabled=(cd_count.get(art.get_nome(), 0) > 0)):
                    data["artistas"] = [a for a in data["artistas"]
                                        if a["nome"] != art.get_nome()]
                    persist()
                    set_flash(f'Artista "{art.get_nome()}" excluído.')
                    st.rerun()
            st.markdown('<hr style="margin:2px 0;border-color:#21262D">', unsafe_allow_html=True)

        if lista and cd_count:
            html('<div class="alert alert-warning" style="margin-top:0.5rem">'
                 '⚠️ Artistas com CDs vinculados não podem ser excluídos.</div>')


# ── CDs ────────────────────────────────────
elif page == "💿  CDs":
    html("""
    <div class="page-header">
        <h1>CDs</h1>
        <p>cadastro e listagem completa</p>
    </div>
    """)
    show_flash()

    nomes_artistas = artista_names(data)
    colecao = build_colecao(data)

    # Cadastrar
    with st.expander("➕ Cadastrar novo CD", expanded=True):
        if not nomes_artistas:
            html('<div class="alert alert-warning">Cadastre ao menos um artista antes de adicionar CDs.</div>')
        else:
            with st.form("form_cd"):
                col1, col2 = st.columns(2)
                with col1:
                    titulo = st.text_input("Título do CD *")
                    ano = st.number_input("Ano de Lançamento *",
                                         min_value=1900, max_value=2100,
                                         value=2000, step=1)
                with col2:
                    artista_sel = st.selectbox("Artista *", nomes_artistas)

                sub = st.form_submit_button("Cadastrar CD")
                if sub:
                    titulo = titulo.strip()
                    erros = []
                    if not titulo:
                        erros.append("Título é obrigatório.")
                    ok_ano, msg_ano = validate_ano(ano)
                    if not ok_ano:
                        erros.append(msg_ano)
                    if erros:
                        for e in erros:
                            html(f'<div class="alert alert-error">{e}</div>')
                    else:
                        ok, msg = colecao.cadastrar_cd(artista_sel, titulo, int(ano))
                        if ok:
                            data["cds"] = colecao.to_list()
                            persist()
                            set_flash(msg)
                            st.rerun()
                        else:
                            html(f'<div class="alert alert-warning">{msg}</div>')

    st.markdown("---")

    todos = colecao.listar_todos()
    html(f'<div style="font-size:1rem;font-weight:700;margin-bottom:0.8rem">'
         f'💿 {len(todos)} CD(s) na coleção</div>')

    if not todos:
        html('<div class="alert alert-info">Nenhum CD cadastrado ainda.</div>')
    else:
        # Ordenação
        col_s, col_o = st.columns([3, 1])
        with col_s:
            busca_lista = st.text_input("🔍 Filtro rápido", placeholder="título ou artista...",
                                        key="filtro_lista")
        with col_o:
            ordem = st.selectbox("Ordenar por", ["Título", "Artista", "Ano"], key="ordem")

        lista = todos
        if busca_lista:
            b = busca_lista.lower()
            lista = [cd for cd in lista
                     if b in cd.get_titulo().lower() or b in cd.get_artista().lower()]

        if ordem == "Título":
            lista = sorted(lista, key=lambda x: x.get_titulo().lower())
        elif ordem == "Artista":
            lista = sorted(lista, key=lambda x: x.get_artista().lower())
        else:
            lista = sorted(lista, key=lambda x: x.get_ano_lancamento())

        for cd in lista:
            html(f"""
            <div class="cd-card">
                <div class="cd-title">💿 {cd.get_titulo()}</div>
                <div class="cd-artist">🎤 {cd.get_artista()}</div>
                <div class="cd-year">📅 {cd.get_ano_lancamento()}</div>
            </div>
            """)


# ── PESQUISAR ──────────────────────────────
elif page == "🔍  Pesquisar":
    html("""
    <div class="page-header">
        <h1>Pesquisar</h1>
        <p>busca por artista ou título</p>
    </div>
    """)
    show_flash()

    colecao = build_colecao(data)
    tab1, tab2 = st.tabs(["🎤 Por Artista", "💿 Por Título"])

    with tab1:
        nome_art = st.text_input("Nome do artista (ou parte)", key="busca_art")
        if nome_art:
            resultados = colecao.pesquisar_por_artista(nome_art)
            html(f'<div class="alert alert-info">'
                 f'{len(resultados)} resultado(s) para artista "{nome_art}"</div>')
            if resultados:
                for cd in resultados:
                    html(f"""
                    <div class="cd-card">
                        <div class="cd-title">💿 {cd.get_titulo()}</div>
                        <div class="cd-artist">🎤 {cd.get_artista()}</div>
                        <div class="cd-year">📅 {cd.get_ano_lancamento()}</div>
                    </div>
                    """)
            else:
                html('<div class="alert alert-warning">Nenhum CD encontrado para este artista.</div>')

    with tab2:
        termo = st.text_input("Parte do título", key="busca_titulo")
        if termo:
            resultados = colecao.pesquisar_por_titulo(termo)
            html(f'<div class="alert alert-info">'
                 f'{len(resultados)} resultado(s) para título "{termo}"</div>')
            if resultados:
                for cd in resultados:
                    html(f"""
                    <div class="cd-card">
                        <div class="cd-title">💿 {cd.get_titulo()}</div>
                        <div class="cd-artist">🎤 {cd.get_artista()}</div>
                        <div class="cd-year">📅 {cd.get_ano_lancamento()}</div>
                    </div>
                    """)
            else:
                html('<div class="alert alert-warning">Nenhum CD encontrado com este título.</div>')


# ── EDITAR / EXCLUIR ───────────────────────
elif page == "✏️  Editar / Excluir":
    html("""
    <div class="page-header">
        <h1>Editar / Excluir</h1>
        <p>gerenciar CDs existentes</p>
    </div>
    """)
    show_flash()

    colecao = build_colecao(data)
    todos = colecao.listar_todos()
    nomes_artistas = artista_names(data)

    if not todos:
        html('<div class="alert alert-info">Nenhum CD cadastrado ainda.</div>')
    else:
        busca = st.text_input("🔍 Filtrar CDs para editar/excluir",
                              placeholder="título ou artista...",
                              key="filtro_edit")
        lista = todos
        if busca:
            b = busca.lower()
            lista = [cd for cd in lista
                     if b in cd.get_titulo().lower() or b in cd.get_artista().lower()]

        if not lista:
            html('<div class="alert alert-warning">Nenhum CD encontrado.</div>')

        for idx_g, cd in enumerate(lista):
            # index real na colecao
            idx_real = todos.index(cd)

            with st.expander(f"💿 {cd.get_titulo()} — {cd.get_artista()} ({cd.get_ano_lancamento()})"):
                tab_edit, tab_del = st.tabs(["✏️ Editar", "🗑️ Excluir"])

                with tab_edit:
                    with st.form(f"form_edit_{idx_real}"):
                        novo_titulo = st.text_input("Título *", value=cd.get_titulo())
                        novo_ano = st.number_input(
                            "Ano *",
                            min_value=1900, max_value=2100,
                            value=cd.get_ano_lancamento(), step=1,
                            key=f"ano_edit_{idx_real}")
                        if nomes_artistas:
                            cur_idx = (nomes_artistas.index(cd.get_artista())
                                       if cd.get_artista() in nomes_artistas else 0)
                            novo_artista = st.selectbox(
                                "Artista *", nomes_artistas,
                                index=cur_idx, key=f"art_edit_{idx_real}")
                        else:
                            novo_artista = cd.get_artista()
                            html('<div class="alert alert-warning">Sem artistas cadastrados.</div>')

                        salvar = st.form_submit_button("💾 Salvar alterações")
                        if salvar:
                            novo_titulo = novo_titulo.strip()
                            erros = []
                            if not novo_titulo:
                                erros.append("Título é obrigatório.")
                            ok_ano, msg_ano = validate_ano(int(novo_ano))
                            if not ok_ano:
                                erros.append(msg_ano)
                            # duplicidade (exceto o próprio)
                            for i2, cd2 in enumerate(todos):
                                if i2 != idx_real:
                                    if (cd2.get_artista().lower() == novo_artista.lower()
                                            and cd2.get_titulo().lower() == novo_titulo.lower()
                                            and cd2.get_ano_lancamento() == int(novo_ano)):
                                        erros.append("Já existe um CD com esses dados.")
                                        break
                            if erros:
                                for e in erros:
                                    html(f'<div class="alert alert-error">{e}</div>')
                            else:
                                todos[idx_real].editar_cd(novo_titulo, int(novo_ano), novo_artista)
                                data["cds"] = [c.to_dict() for c in todos]
                                persist()
                                set_flash(f'CD "{novo_titulo}" atualizado com sucesso!')
                                st.rerun()

                with tab_del:
                    html(f"""
                    <div class="alert alert-warning" style="margin-bottom:1rem">
                        ⚠️ Você está prestes a excluir permanentemente:<br>
                        <strong>{cd.get_titulo()}</strong> — {cd.get_artista()} ({cd.get_ano_lancamento()})
                    </div>
                    """)
                    if st.button("🗑️ Confirmar exclusão",
                                 key=f"confirm_del_{idx_real}",
                                 type="primary"):
                        titulo_excluido = cd.get_titulo()
                        colecao.excluir_cd(cd)
                        data["cds"] = colecao.to_list()
                        persist()
                        set_flash(f'CD "{titulo_excluido}" excluído com sucesso!', "success")
                        st.rerun()