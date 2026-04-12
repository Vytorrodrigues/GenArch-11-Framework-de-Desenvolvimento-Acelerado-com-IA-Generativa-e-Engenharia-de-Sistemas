"""
Lista de Compras - Aplicação Streamlit (Tema Escuro)
"""

import streamlit as st
import json
import os
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import datetime

# ─────────────────────────────────────────────
#  DOMÍNIO / ENTIDADES
# ─────────────────────────────────────────────

class UnidadeCompra(str, Enum):
    PACOTE = "PACOTE"
    KG = "KG"
    LITRO = "LITRO"
    CAIXA = "CAIXA"
    UNIDADE = "UNIDADE"

class Mes(str, Enum):
    JANEIRO = "JANEIRO"
    FEVEREIRO = "FEVEREIRO"
    MARCO = "MARÇO"
    ABRIL = "ABRIL"
    MAIO = "MAIO"
    JUNHO = "JUNHO"
    JULHO = "JULHO"
    AGOSTO = "AGOSTO"
    SETEMBRO = "SETEMBRO"
    OUTUBRO = "OUTUBRO"
    NOVEMBRO = "NOVEMBRO"
    DEZEMBRO = "DEZEMBRO"

    @classmethod
    def from_month_number(cls, n: int) -> "Mes":
        return list(cls)[n - 1]

    def to_number(self) -> int:
        return list(Mes).index(self) + 1


@dataclass
class Produto:
    id: int
    nome: str
    unidade: str

    def to_dict(self): return asdict(self)

    @staticmethod
    def from_dict(d): return Produto(id=d["id"], nome=d["nome"], unidade=d["unidade"])


@dataclass
class Periodo:
    ano: int
    mes: str

    @staticmethod
    def new(ano, mes): return Periodo(ano=ano, mes=mes)

    def label(self): return f"{self.mes}/{self.ano}"

    def to_dict(self): return asdict(self)

    @staticmethod
    def from_dict(d): return Periodo(ano=d["ano"], mes=d["mes"])

    def __eq__(self, o): return isinstance(o, Periodo) and self.ano == o.ano and self.mes == o.mes

    def __hash__(self): return hash((self.ano, self.mes))


@dataclass
class ItemLista:
    produto_id: int
    qtd_prev: float
    qtd_comp: float
    preco_est: float

    @property
    def subtotal_estimado(self): return round(self.qtd_comp * self.preco_est, 2)

    def to_dict(self):
        return {"produto_id": self.produto_id, "qtd_prev": self.qtd_prev,
                "qtd_comp": self.qtd_comp, "preco_est": self.preco_est}

    @staticmethod
    def from_dict(d):
        return ItemLista(produto_id=d["produto_id"], qtd_prev=d["qtd_prev"],
                         qtd_comp=d["qtd_comp"], preco_est=d["preco_est"])


@dataclass
class ListaCompras:
    id: int
    periodo: Periodo
    itens: List[ItemLista] = field(default_factory=list)

    @staticmethod
    def criar_lista_mes(periodo, lista_id): return ListaCompras(id=lista_id, periodo=periodo)

    @property
    def total_mensal(self): return round(sum(i.subtotal_estimado for i in self.itens), 2)

    def to_dict(self):
        return {"id": self.id, "periodo": self.periodo.to_dict(),
                "itens": [i.to_dict() for i in self.itens]}

    @staticmethod
    def from_dict(d):
        return ListaCompras(id=d["id"], periodo=Periodo.from_dict(d["periodo"]),
                            itens=[ItemLista.from_dict(i) for i in d.get("itens", [])])


# ─────────────────────────────────────────────
#  PERSISTÊNCIA
# ─────────────────────────────────────────────

DATA_FILE = "lista_compras_data.json"

MOCK_DATA = {
    "produtos": [
        {"id": 1, "nome": "Arroz", "unidade": "KG"},
        {"id": 2, "nome": "Feijão", "unidade": "KG"},
        {"id": 3, "nome": "Óleo de Soja", "unidade": "LITRO"},
        {"id": 4, "nome": "Açúcar", "unidade": "PACOTE"},
        {"id": 5, "nome": "Leite Integral", "unidade": "CAIXA"},
        {"id": 6, "nome": "Macarrão", "unidade": "PACOTE"},
        {"id": 7, "nome": "Café", "unidade": "PACOTE"},
        {"id": 8, "nome": "Sabão em Pó", "unidade": "UNIDADE"},
    ],
    "listas": [
        {
            "id": 1,
            "periodo": {"ano": 2025, "mes": "ABRIL"},
            "itens": [
                {"produto_id": 1, "qtd_prev": 5.0, "qtd_comp": 5.0, "preco_est": 6.50},
                {"produto_id": 2, "qtd_prev": 2.0, "qtd_comp": 2.0, "preco_est": 8.90},
                {"produto_id": 3, "qtd_prev": 2.0, "qtd_comp": 2.0, "preco_est": 7.20},
                {"produto_id": 5, "qtd_prev": 12.0, "qtd_comp": 12.0, "preco_est": 4.50},
            ],
        },
        {
            "id": 2,
            "periodo": {"ano": 2025, "mes": "MAIO"},
            "itens": [
                {"produto_id": 1, "qtd_prev": 5.0, "qtd_comp": 5.0, "preco_est": 6.80},
                {"produto_id": 4, "qtd_prev": 3.0, "qtd_comp": 3.0, "preco_est": 3.90},
                {"produto_id": 7, "qtd_prev": 2.0, "qtd_comp": 2.0, "preco_est": 14.00},
            ],
        },
    ],
    "next_produto_id": 9,
    "next_lista_id": 3,
}


def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(MOCK_DATA)
        return MOCK_DATA
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_produtos(data): return [Produto.from_dict(p) for p in data["produtos"]]
def get_listas(data): return [ListaCompras.from_dict(l) for l in data["listas"]]
def produto_map(data): return {p["id"]: Produto.from_dict(p) for p in data["produtos"]}


# ─────────────────────────────────────────────
#  CONFIG & DARK THEME CSS
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Lista de Compras",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg:       #0d1117;
    --surface:  #161b22;
    --card:     #1c2330;
    --hover:    #21293a;
    --border:   #30363d;
    --t1:       #e6edf3;
    --t2:       #8b949e;
    --t3:       #6e7681;
    --accent:   #58a6ff;
    --adim:     #1f3a5f;
    --green:    #3fb950;
    --gdim:     #1a3a22;
    --red:      #f85149;
    --yellow:   #d29922;
    --ydim:     #2d2200;
}

/* ── BASE ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--t1) !important;
}
.main .block-container {
    background: var(--bg) !important;
    padding-top: 2rem;
    max-width: 1100px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--t1) !important; }
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] button {
    background: var(--card) !important;
    color: var(--t1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] button:hover {
    background: var(--hover) !important;
    border-color: var(--accent) !important;
}

/* ── MAIN BUTTONS ── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}
button[kind="primary"], .stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #0d1117 !important;
    border: none !important;
}
button[kind="primary"]:hover { background: #79c0ff !important; }
.stButton > button[kind="secondary"],
.stButton > button:not([kind="primary"]) {
    background: var(--card) !important;
    color: var(--t1) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: var(--hover) !important;
    border-color: var(--accent) !important;
}

/* ── INPUTS ── */
input[type="text"], input[type="number"],
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: var(--card) !important;
    color: var(--t1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    caret-color: var(--accent) !important;
}
input:focus { border-color: var(--accent) !important; outline: none !important; }

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--t1) !important;
}
[data-baseweb="popover"] { background: var(--card) !important; }
[data-baseweb="menu"] { background: var(--card) !important; border: 1px solid var(--border) !important; }
[role="option"] { background: var(--card) !important; color: var(--t1) !important; }
[role="option"]:hover { background: var(--hover) !important; }
[role="option"][aria-selected="true"] { background: var(--adim) !important; color: var(--accent) !important; }

/* Labels */
label, p, [data-testid="stWidgetLabel"] p {
    color: var(--t2) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] details summary {
    background: var(--surface) !important;
    color: var(--t1) !important;
    font-weight: 500 !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] details[open] summary { border-bottom: 1px solid var(--border) !important; }
[data-testid="stExpander"] details summary:hover { background: var(--hover) !important; }
[data-testid="stExpander"] .streamlit-expanderContent {
    background: var(--surface) !important;
    padding: 1rem !important;
}
/* Expander arrow */
[data-testid="stExpander"] summary svg { fill: var(--t2) !important; }

/* ── FORMS ── */
[data-testid="stForm"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.25rem !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"], .stInfo, .stWarning, .stError, .stSuccess {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--t1) !important;
    border-radius: 8px !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ── MARKDOWN ── */
.stMarkdown, .stMarkdown p, .stMarkdown span { color: var(--t1) !important; }
.stMarkdown strong { color: var(--t1) !important; font-weight: 600 !important; }

/* Number input buttons */
[data-testid="stNumberInput"] button {
    background: var(--hover) !important;
    color: var(--t1) !important;
    border: none !important;
}

/* ── CUSTOM COMPONENTS ── */
.ph { font-size:1.55rem; font-weight:700; color:var(--t1); margin-bottom:.15rem; }
.ps { font-size:.875rem; color:var(--t2); margin-bottom:1.4rem; }

.mcard {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
}
.ml { font-size:.7rem; font-weight:600; text-transform:uppercase; letter-spacing:.09em; color:var(--t3); margin-bottom:.35rem; }
.mv { font-size:1.9rem; font-weight:700; color:var(--t1); }
.mv.blue  { color: var(--accent); }
.mv.green { color: var(--green); }

.tbar {
    background: linear-gradient(135deg,#0c2340,#1a3a5c);
    border: 1px solid var(--adim);
    border-radius:12px;
    padding:1.1rem 1.5rem;
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:1rem;
}
.tbar-l { font-size:.7rem; text-transform:uppercase; letter-spacing:.09em; color:#79c0ff; margin-bottom:.25rem; }
.tbar-v { font-size:1.85rem; font-weight:700; color:#fff; }

.dt { width:100%; border-collapse:collapse; font-size:.875rem; color:var(--t1); }
.dt th { background:var(--bg); color:var(--t3); font-size:.7rem; font-weight:600;
    text-transform:uppercase; letter-spacing:.07em; padding:.5rem 1rem;
    text-align:left; border-bottom:1px solid var(--border); }
.dt td { padding:.75rem 1rem; border-bottom:1px solid var(--border); }
.dt tr:last-child td { border-bottom:none; }
.dt tr:hover td { background:var(--hover); }
.sub { color:var(--green); font-weight:600; }

.badge { display:inline-block; padding:.18rem .55rem; border-radius:20px;
    font-size:.7rem; font-weight:600; background:var(--adim); color:var(--accent); }
.badge.g { background:var(--gdim); color:var(--green); }
.badge.x { background:var(--hover); color:var(--t2); }

.fok  { background:var(--gdim); border:1px solid var(--green); border-radius:8px;
    padding:.6rem 1rem; color:var(--green); font-weight:500; font-size:.875rem; margin-bottom:.75rem; }
.fwn  { background:var(--ydim); border:1px solid var(--yellow); border-radius:8px;
    padding:.6rem 1rem; color:var(--yellow); font-weight:500; font-size:.875rem; margin-bottom:.75rem; }
.ferr { background:#2d1a1a; border:1px solid var(--red); border-radius:8px;
    padding:.6rem 1rem; color:var(--red); font-weight:500; font-size:.875rem; margin-bottom:.75rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ESTADO
# ─────────────────────────────────────────────

if "data"              not in st.session_state: st.session_state.data              = load_data()
if "page"              not in st.session_state: st.session_state.page              = "Dashboard"
if "selected_lista_id" not in st.session_state: st.session_state.selected_lista_id = None
if "flash"             not in st.session_state: st.session_state.flash             = None
if "flash_type"        not in st.session_state: st.session_state.flash_type        = "success"


def flash(msg, kind="success"):
    st.session_state.flash = msg
    st.session_state.flash_type = kind


def render_flash():
    if st.session_state.flash:
        cls = {"success": "fok", "warn": "fwn", "error": "ferr"}.get(st.session_state.flash_type, "fok")
        ico = "✓" if cls == "fok" else "⚠" if cls == "fwn" else "✕"
        st.markdown(f'<div class="{cls}">{ico}  {st.session_state.flash}</div>', unsafe_allow_html=True)
        st.session_state.flash = None


def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def mes_opts(): return [m.value for m in Mes]
def uni_opts(): return [u.value for u in UnidadeCompra]


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🛒 Lista de Compras")
    st.markdown("---")

    for key, icon, label in [
        ("Dashboard", "📊", "Dashboard"),
        ("Listas",    "📋", "Listas de Compras"),
        ("Produtos",  "📦", "Produtos"),
    ]:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.session_state.selected_lista_id = None
            st.rerun()

    st.markdown("---")
    now = datetime.datetime.now()
    if st.button("➕  Nova Lista do Mês Atual", use_container_width=True):
        data = st.session_state.data
        mes_atual = Mes.from_month_number(now.month).value
        periodo = Periodo.new(now.year, mes_atual)
        listas = get_listas(data)
        if any(l.periodo == periodo for l in listas):
            flash(f"Lista {periodo.label()} já existe.", "warn")
        else:
            nova = ListaCompras.criar_lista_mes(periodo, data["next_lista_id"])
            data["next_lista_id"] += 1
            data["listas"].append(nova.to_dict())
            save_data(data)
            st.session_state.data = data
            st.session_state.selected_lista_id = nova.id
            flash(f"Lista {periodo.label()} criada!")
        st.session_state.page = "Listas"
        st.rerun()

    st.markdown("---")
    st.markdown('<small style="color:#6e7681">© 2025 Lista de Compras</small>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

def page_dashboard():
    data = st.session_state.data
    listas = get_listas(data)
    pmap   = produto_map(data)

    st.markdown('<div class="ph">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="ps">Visão geral das suas listas e produtos cadastrados.</div>', unsafe_allow_html=True)
    render_flash()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="mcard"><div class="ml">Listas de Compras</div>'
                    f'<div class="mv blue">{len(listas)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="mcard"><div class="ml">Produtos Cadastrados</div>'
                    f'<div class="mv">{len(get_produtos(data))}</div></div>', unsafe_allow_html=True)
    with c3:
        total = sum(l.total_mensal for l in listas)
        st.markdown(f'<div class="mcard"><div class="ml">Total Acumulado</div>'
                    f'<div class="mv green">{fmt(total)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>**Resumo por Lista**", unsafe_allow_html=True)

    if not listas:
        st.info("Nenhuma lista cadastrada ainda.")
        return

    for lista in sorted(listas, key=lambda l: (l.periodo.ano, Mes[l.periodo.mes].to_number()), reverse=True):
        with st.expander(f"📋  {lista.periodo.label()}  —  {fmt(lista.total_mensal)}"):
            if not lista.itens:
                st.markdown('<span style="color:var(--t2)">Lista vazia.</span>', unsafe_allow_html=True)
            else:
                rows = "".join(f"""<tr>
                    <td>{pmap[i.produto_id].nome if i.produto_id in pmap else f'#{i.produto_id}'}</td>
                    <td><span class="badge x">{pmap[i.produto_id].unidade if i.produto_id in pmap else '-'}</span></td>
                    <td>{i.qtd_prev}</td><td>{i.qtd_comp}</td>
                    <td>{fmt(i.preco_est)}</td>
                    <td class="sub">{fmt(i.subtotal_estimado)}</td>
                </tr>""" for i in lista.itens)
                st.markdown(f"""<table class="dt">
                <thead><tr><th>Produto</th><th>Unidade</th><th>Qtd Prev.</th>
                <th>Qtd Comp.</th><th>Preço Est.</th><th>Subtotal</th></tr></thead>
                <tbody>{rows}</tbody></table>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Abrir lista", key=f"open_{lista.id}"):
                st.session_state.selected_lista_id = lista.id
                st.session_state.page = "Listas"
                st.rerun()


# ─────────────────────────────────────────────
#  LISTAS
# ─────────────────────────────────────────────

def page_listas():
    data  = st.session_state.data
    listas = get_listas(data)
    pmap  = produto_map(data)

    st.markdown('<div class="ph">📋 Listas de Compras</div>', unsafe_allow_html=True)
    st.markdown('<div class="ps">Crie e gerencie suas listas mensais.</div>', unsafe_allow_html=True)
    render_flash()

    with st.expander("➕  Criar nova lista"):
        with st.form("nova_lista"):
            c1, c2 = st.columns(2)
            with c1: ano_v = st.number_input("Ano", min_value=2000, max_value=2100,
                                              value=datetime.datetime.now().year, step=1)
            with c2: mes_v = st.selectbox("Mês", mes_opts())
            if st.form_submit_button("Criar Lista", type="primary"):
                p = Periodo.new(int(ano_v), mes_v)
                if any(l.periodo == p for l in listas):
                    flash(f"Lista {p.label()} já existe.", "warn")
                else:
                    nova = ListaCompras.criar_lista_mes(p, data["next_lista_id"])
                    data["next_lista_id"] += 1
                    data["listas"].append(nova.to_dict())
                    save_data(data); st.session_state.data = data
                    st.session_state.selected_lista_id = nova.id
                    flash(f"Lista {p.label()} criada!")
                st.rerun()

    if not listas:
        st.info("Nenhuma lista cadastrada.")
        return

    ids = [l.id for l in sorted(listas, key=lambda x: (x.periodo.ano, Mes[x.periodo.mes].to_number()), reverse=True)]
    labels = {l.id: f"{l.periodo.label()}  —  {fmt(l.total_mensal)}" for l in listas}

    if st.session_state.selected_lista_id not in ids:
        st.session_state.selected_lista_id = ids[0]

    chosen = st.selectbox("Selecionar lista", ids,
                          format_func=lambda x: labels[x],
                          index=ids.index(st.session_state.selected_lista_id))
    st.session_state.selected_lista_id = chosen

    data  = st.session_state.data
    pmap  = produto_map(data)
    lista = next((ListaCompras.from_dict(l) for l in data["listas"] if l["id"] == chosen), None)
    if not lista: return

    st.markdown(f"""<div class="tbar">
        <div><div class="tbar-l">Total Estimado do Mês</div>
        <div class="tbar-v">{fmt(lista.total_mensal)}</div></div>
        <div style="font-size:2.2rem">🧾</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("**Itens da lista**")
    if lista.itens:
        rows = "".join(f"""<tr>
            <td>{pmap[i.produto_id].nome if i.produto_id in pmap else f'#{i.produto_id}'}</td>
            <td><span class="badge x">{pmap[i.produto_id].unidade if i.produto_id in pmap else '-'}</span></td>
            <td>{i.qtd_prev}</td><td>{i.qtd_comp}</td>
            <td>{fmt(i.preco_est)}</td>
            <td class="sub">{fmt(i.subtotal_estimado)}</td>
        </tr>""" for i in lista.itens)
        st.markdown(f"""<table class="dt">
        <thead><tr><th>Produto</th><th>Unidade</th><th>Qtd Prev.</th>
        <th>Qtd Comp.</th><th>Preço Est.</th><th>Subtotal</th></tr></thead>
        <tbody>{rows}</tbody></table><br/>""", unsafe_allow_html=True)
    else:
        st.info("Lista vazia. Adicione produtos abaixo.")

    todos = get_produtos(data)
    ids_na_lista = {i.produto_id for i in lista.itens}
    disponiveis = [p for p in todos if p.id not in ids_na_lista]

    with st.expander("➕  Adicionar produto à lista", expanded=len(lista.itens) == 0):
        if not disponiveis:
            st.markdown('<span style="color:var(--t2)">Todos os produtos já estão na lista.</span>', unsafe_allow_html=True)
        else:
            with st.form(f"add_{lista.id}"):
                pm = {p.id: f"{p.nome}  ({p.unidade})" for p in disponiveis}
                pid = st.selectbox("Produto", list(pm.keys()), format_func=lambda x: pm[x])
                c1, c2, c3 = st.columns(3)
                with c1: qp = st.number_input("Qtd Prevista",   min_value=0.0, value=1.0, step=0.5)
                with c2: qc = st.number_input("Qtd a Comprar",  min_value=0.0, value=1.0, step=0.5)
                with c3: pe = st.number_input("Preço Est. (R$)", min_value=0.0, value=0.0, step=0.10, format="%.2f")
                if st.form_submit_button("Adicionar", type="primary"):
                    if qp < 0 or qc < 0 or pe < 0:
                        flash("Valores devem ser ≥ 0.", "error")
                    else:
                        for l in data["listas"]:
                            if l["id"] == lista.id:
                                l["itens"].append({"produto_id": pid, "qtd_prev": qp,
                                                   "qtd_comp": qc, "preco_est": pe}); break
                        save_data(data); st.session_state.data = data
                        flash("Produto adicionado!")
                    st.rerun()

    if lista.itens:
        st.markdown("**✏️ Editar / Remover Itens**")
        for item in lista.itens:
            nome = pmap[item.produto_id].nome if item.produto_id in pmap else f"#{item.produto_id}"
            with st.expander(f"🔹  {nome}  —  {fmt(item.subtotal_estimado)}"):
                with st.form(f"ed_{lista.id}_{item.produto_id}"):
                    c1, c2, c3 = st.columns(3)
                    with c1: nqp = st.number_input("Qtd Prevista",   min_value=0.0, value=float(item.qtd_prev),  step=0.5)
                    with c2: nqc = st.number_input("Qtd a Comprar",  min_value=0.0, value=float(item.qtd_comp),  step=0.5)
                    with c3: npe = st.number_input("Preço Est. (R$)", min_value=0.0, value=float(item.preco_est), step=0.10, format="%.2f")
                    cs, cd = st.columns([3, 1])
                    with cs: salvar  = st.form_submit_button("💾 Salvar",  type="primary")
                    with cd: remover = st.form_submit_button("🗑️ Remover")
                    if salvar:
                        for l in data["listas"]:
                            if l["id"] == lista.id:
                                for it in l["itens"]:
                                    if it["produto_id"] == item.produto_id:
                                        it.update({"qtd_prev": nqp, "qtd_comp": nqc, "preco_est": npe}); break
                                break
                        save_data(data); st.session_state.data = data
                        flash(f"'{nome}' atualizado!"); st.rerun()
                    if remover:
                        for l in data["listas"]:
                            if l["id"] == lista.id:
                                l["itens"] = [it for it in l["itens"] if it["produto_id"] != item.produto_id]; break
                        save_data(data); st.session_state.data = data
                        flash(f"'{nome}' removido.", "warn"); st.rerun()

    st.markdown("---")
    with st.expander("⚠️  Excluir esta lista"):
        st.markdown(f'<span style="color:var(--red)">Excluir <strong>{lista.periodo.label()}</strong>? Irreversível.</span>',
                    unsafe_allow_html=True)
        if st.button("Confirmar exclusão", type="primary", key=f"del_{lista.id}"):
            data["listas"] = [l for l in data["listas"] if l["id"] != lista.id]
            save_data(data); st.session_state.data = data
            st.session_state.selected_lista_id = None
            flash(f"Lista {lista.periodo.label()} excluída.", "warn"); st.rerun()


# ─────────────────────────────────────────────
#  PRODUTOS
# ─────────────────────────────────────────────

def page_produtos():
    data    = st.session_state.data
    produtos = get_produtos(data)

    st.markdown('<div class="ph">📦 Produtos</div>', unsafe_allow_html=True)
    st.markdown('<div class="ps">Gerencie o catálogo de produtos cadastrados.</div>', unsafe_allow_html=True)
    render_flash()

    with st.expander("➕  Cadastrar novo produto"):
        with st.form("novo_prod"):
            c1, c2 = st.columns(2)
            with c1: nome    = st.text_input("Nome do produto*")
            with c2: unidade = st.selectbox("Unidade*", uni_opts())
            if st.form_submit_button("Cadastrar", type="primary"):
                nome = nome.strip()
                if not nome:
                    flash("Nome é obrigatório.", "error")
                elif any(p.nome.lower() == nome.lower() for p in produtos):
                    flash(f"'{nome}' já existe.", "warn")
                else:
                    data["produtos"].append({"id": data["next_produto_id"], "nome": nome, "unidade": unidade})
                    data["next_produto_id"] += 1
                    save_data(data); st.session_state.data = data
                    flash(f"'{nome}' cadastrado!")
                st.rerun()

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    filtro   = st.text_input("🔍 Filtrar por nome", placeholder="Digite para filtrar...")
    filtrados = [p for p in produtos if filtro.lower() in p.nome.lower()] if filtro else produtos
    st.markdown(f'<span style="color:var(--t3);font-size:.82rem">{len(filtrados)} produto(s)</span><br/>',
                unsafe_allow_html=True)

    for prod in filtrados:
        with st.expander(f"🔹  {prod.nome}  —  {prod.unidade}"):
            with st.form(f"ep_{prod.id}"):
                c1, c2 = st.columns(2)
                with c1: nn = st.text_input("Nome*", value=prod.nome)
                with c2: nu = st.selectbox("Unidade*", uni_opts(), index=uni_opts().index(prod.unidade))
                cs, cd = st.columns([3, 1])
                with cs: salvar  = st.form_submit_button("💾 Salvar",  type="primary")
                with cd: excluir = st.form_submit_button("🗑️ Excluir")
                if salvar:
                    nn = nn.strip()
                    if not nn:
                        flash("Nome é obrigatório.", "error")
                    else:
                        for p in data["produtos"]:
                            if p["id"] == prod.id: p["nome"] = nn; p["unidade"] = nu; break
                        save_data(data); st.session_state.data = data
                        flash(f"'{nn}' atualizado!")
                    st.rerun()
                if excluir:
                    em_uso = any(any(it["produto_id"] == prod.id for it in l["itens"]) for l in data["listas"])
                    if em_uso:
                        flash(f"'{prod.nome}' está em uso em uma lista.", "error")
                    else:
                        data["produtos"] = [p for p in data["produtos"] if p["id"] != prod.id]
                        save_data(data); st.session_state.data = data
                        flash(f"'{prod.nome}' excluído.", "warn")
                    st.rerun()


# ─────────────────────────────────────────────
#  ROTEADOR
# ─────────────────────────────────────────────

{"Dashboard": page_dashboard, "Listas": page_listas, "Produtos": page_produtos}.get(
    st.session_state.page, page_dashboard
)()