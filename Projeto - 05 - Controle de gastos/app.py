"""
Controle de Gastos - Aplicação Streamlit
Baseado no diagrama de classes UML e requisitos funcionais/não funcionais
"""

import streamlit as st
import json
import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum
import uuid

# ──────────────────────────────────────────────
# DOMÍNIO: Entidades e Enumerações
# ──────────────────────────────────────────────

class FormaPagamento(str, Enum):
    DINHEIRO = "Dinheiro"
    CARTAO_CREDITO = "Cartão de Crédito"
    CARTAO_DEBITO = "Cartão de Débito"
    TICKET_ALIMENTACAO = "Ticket Alimentação"
    CHEQUE = "Cheque"


@dataclass
class Periodo:
    dataInicio: date
    dataFim: date

    @classmethod
    def new(cls, inicio: date, fim: date) -> "Periodo":
        return cls(dataInicio=inicio, dataFim=fim)

    def contem(self, data: date) -> bool:
        return self.dataInicio <= data <= self.dataFim


@dataclass
class Gasto:
    tipo: str
    data: date
    valor: float
    forma: FormaPagamento
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def cadastrar(self, tipo: str, data: date, valor: float, forma: FormaPagamento):
        self.tipo = tipo
        self.data = data
        self.valor = valor
        self.forma = forma

    def editar(self, tipo: str, data: date, valor: float, forma: FormaPagamento):
        self.tipo = tipo
        self.data = data
        self.valor = valor
        self.forma = forma

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "data": self.data.isoformat(),
            "valor": self.valor,
            "forma": self.forma.value if isinstance(self.forma, FormaPagamento) else self.forma,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Gasto":
        return cls(
            id=d["id"],
            tipo=d["tipo"],
            data=date.fromisoformat(d["data"]),
            valor=float(d["valor"]),
            forma=FormaPagamento(d["forma"]),
        )


class RelatorioGastos:
    def __init__(self, periodo: Periodo, todos_gastos: list[Gasto]):
        self.periodo = periodo
        self._todos = todos_gastos

    @property
    def gastosNoPeriodo(self) -> list[Gasto]:
        return [g for g in self._todos if self.periodo.contem(g.data)]

    def listarGastosNoPeriodo(self) -> list[Gasto]:
        return sorted(self.gastosNoPeriodo, key=lambda g: g.data)

    def totalMensal(self) -> float:
        return sum(g.valor for g in self.gastosNoPeriodo)

    def agruparPorTipo(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for g in self.gastosNoPeriodo:
            result[g.tipo] = result.get(g.tipo, 0.0) + g.valor
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    def agruparPorFormaPagamento(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for g in self.gastosNoPeriodo:
            k = g.forma.value if isinstance(g.forma, FormaPagamento) else g.forma
            result[k] = result.get(k, 0.0) + g.valor
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    def exportarCSV(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Tipo", "Data", "Valor (R$)", "Forma de Pagamento"])
        for g in self.listarGastosNoPeriodo():
            writer.writerow([
                g.id,
                g.tipo,
                g.data.strftime("%d/%m/%Y"),
                f"{g.valor:.2f}",
                g.forma.value if isinstance(g.forma, FormaPagamento) else g.forma,
            ])
        return output.getvalue()


# ──────────────────────────────────────────────
# PERSISTÊNCIA: JSON em st.session_state
# ──────────────────────────────────────────────

STORAGE_KEY = "gastos_data"
TIPOS_PADRAO = ["Remédio", "Roupa", "Comida", "Transporte", "Lazer", "Educação", "Saúde", "Outros"]

MOCK_DATA = [
    {"id": "mock-1", "tipo": "Comida", "data": "2026-03-05", "valor": 150.00, "forma": "Dinheiro"},
    {"id": "mock-2", "tipo": "Remédio", "data": "2026-03-10", "valor": 89.90, "forma": "Cartão de Crédito"},
    {"id": "mock-3", "tipo": "Roupa", "data": "2026-03-15", "valor": 320.00, "forma": "Cartão de Débito"},
    {"id": "mock-4", "tipo": "Transporte", "data": "2026-03-18", "valor": 45.50, "forma": "Ticket Alimentação"},
    {"id": "mock-5", "tipo": "Lazer", "data": "2026-03-22", "valor": 120.00, "forma": "Cheque"},
    {"id": "mock-6", "tipo": "Comida", "data": "2026-04-02", "valor": 210.75, "forma": "Cartão de Débito"},
    {"id": "mock-7", "tipo": "Saúde", "data": "2026-04-05", "valor": 180.00, "forma": "Cartão de Crédito"},
    {"id": "mock-8", "tipo": "Educação", "data": "2026-04-08", "valor": 99.90, "forma": "Dinheiro"},
]


def init_storage():
    if STORAGE_KEY not in st.session_state:
        st.session_state[STORAGE_KEY] = [Gasto.from_dict(d) for d in MOCK_DATA]


def get_gastos() -> list[Gasto]:
    return st.session_state.get(STORAGE_KEY, [])


def save_gasto(gasto: Gasto):
    gastos = get_gastos()
    gastos.append(gasto)
    st.session_state[STORAGE_KEY] = gastos


def update_gasto(gasto_id: str, tipo: str, data: date, valor: float, forma: FormaPagamento):
    gastos = get_gastos()
    for g in gastos:
        if g.id == gasto_id:
            g.editar(tipo, data, valor, forma)
            break
    st.session_state[STORAGE_KEY] = gastos


def delete_gasto(gasto_id: str):
    gastos = [g for g in get_gastos() if g.id != gasto_id]
    st.session_state[STORAGE_KEY] = gastos


def find_gasto(gasto_id: str) -> Optional[Gasto]:
    return next((g for g in get_gastos() if g.id == gasto_id), None)


# ──────────────────────────────────────────────
# VALIDAÇÕES (NRF03)
# ──────────────────────────────────────────────

def validar_gasto(tipo: str, data_val, valor_str: str, forma: str) -> list[str]:
    erros = []
    if not tipo or tipo.strip() == "":
        erros.append("Tipo de gasto é obrigatório.")
    if data_val is None:
        erros.append("Data é obrigatória.")
    try:
        valor = float(valor_str)
        if valor <= 0:
            erros.append("Valor deve ser maior que zero.")
    except (ValueError, TypeError):
        erros.append("Valor inválido.")
    if not forma:
        erros.append("Forma de pagamento é obrigatória.")
    return erros


# ──────────────────────────────────────────────
# INTERFACE: Configuração de Página e Estilo
# ──────────────────────────────────────────────

def configurar_pagina():
    st.set_page_config(
        page_title="Controle de Gastos",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3, .stMetric label, .sidebar-title {
        font-family: 'Syne', sans-serif !important;
    }

    .stApp {
        background: #0f0f13;
        color: #e8e4dc;
    }

    section[data-testid="stSidebar"] {
        background: #16161d !important;
        border-right: 1px solid #2a2a35;
    }

    section[data-testid="stSidebar"] * {
        color: #c8c4bc !important;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    /* Cards de métricas */
    [data-testid="metric-container"] {
        background: #1a1a24;
        border: 1px solid #2e2e3e;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.6rem !important;
        color: #f0c060 !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #888 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Botões */
    .stButton > button {
        background: #f0c060;
        color: #0f0f13;
        border: none;
        border-radius: 8px;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.04em;
        padding: 0.5rem 1.2rem;
        transition: all 0.18s ease;
    }

    .stButton > button:hover {
        background: #ffd580;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(240,192,96,0.35);
    }

    .stButton > button[kind="secondary"] {
        background: #2a2a35;
        color: #c8c4bc;
    }

    /* Formulários */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: #1a1a24 !important;
        border: 1px solid #2e2e3e !important;
        border-radius: 8px !important;
        color: #e8e4dc !important;
    }

    .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #888 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    /* Tabela */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #2e2e3e;
    }

    /* Alerts */
    .stAlert {
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border-color: #2a2a35;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #16161d;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #888;
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        border-radius: 7px;
    }
    .stTabs [aria-selected="true"] {
        background: #f0c060 !important;
        color: #0f0f13 !important;
    }

    /* Page title */
    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #e8e4dc;
        margin-bottom: 0.2rem;
    }
    .page-subtitle {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    /* Gasto card */
    .gasto-card {
        background: #1a1a24;
        border: 1px solid #2e2e3e;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }

    /* Badge */
    .badge {
        display: inline-block;
        background: #252530;
        border: 1px solid #3a3a4a;
        color: #a8a4b0;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-family: 'Syne', sans-serif;
    }

    .badge-gold {
        background: rgba(240,192,96,0.12);
        border-color: rgba(240,192,96,0.3);
        color: #f0c060;
    }

    /* Sidebar nav */
    .nav-item {
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PÁGINAS
# ──────────────────────────────────────────────

def pagina_dashboard():
    st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visão geral dos seus gastos</div>', unsafe_allow_html=True)

    gastos = get_gastos()

    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    periodo_mes = Periodo.new(inicio_mes, hoje)
    relatorio_mes = RelatorioGastos(periodo_mes, gastos)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total do Mês", f"R$ {relatorio_mes.totalMensal():,.2f}")
    with col2:
        st.metric("Gastos no Mês", len(relatorio_mes.gastosNoPeriodo))
    with col3:
        st.metric("Total de Registros", len(gastos))
    with col4:
        media = relatorio_mes.totalMensal() / max(len(relatorio_mes.gastosNoPeriodo), 1)
        st.metric("Ticket Médio", f"R$ {media:,.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Por Tipo (mês atual)")
        por_tipo = relatorio_mes.agruparPorTipo()
        if por_tipo:
            total = sum(por_tipo.values())
            for tipo, val in por_tipo.items():
                pct = val / total * 100
                st.markdown(
                    f'<div class="gasto-card" style="display:flex;justify-content:space-between;align-items:center">'
                    f'<span>{tipo}</span>'
                    f'<div>'
                    f'<span class="badge">{pct:.1f}%</span>&nbsp;'
                    f'<span style="color:#f0c060;font-family:Syne,sans-serif;font-weight:700">R$ {val:,.2f}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Nenhum gasto no mês atual.")

    with col_b:
        st.markdown("#### Por Forma de Pagamento (mês atual)")
        por_forma = relatorio_mes.agruparPorFormaPagamento()
        if por_forma:
            total = sum(por_forma.values())
            for forma, val in por_forma.items():
                pct = val / total * 100
                st.markdown(
                    f'<div class="gasto-card" style="display:flex;justify-content:space-between;align-items:center">'
                    f'<span>{forma}</span>'
                    f'<div>'
                    f'<span class="badge">{pct:.1f}%</span>&nbsp;'
                    f'<span style="color:#f0c060;font-family:Syne,sans-serif;font-weight:700">R$ {val:,.2f}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Nenhum gasto no mês atual.")

    st.markdown("---")
    st.markdown("#### Últimos 5 Gastos")
    recentes = sorted(gastos, key=lambda g: g.data, reverse=True)[:5]
    if recentes:
        for g in recentes:
            st.markdown(
                f'<div class="gasto-card" style="display:flex;justify-content:space-between;align-items:center">'
                f'<div>'
                f'<span style="font-family:Syne,sans-serif;font-weight:700">{g.tipo}</span>'
                f'&nbsp;<span class="badge">{g.forma.value}</span>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<span style="color:#f0c060;font-family:Syne,sans-serif;font-weight:700">R$ {g.valor:,.2f}</span>'
                f'<br><span style="color:#555;font-size:0.8rem">{g.data.strftime("%d/%m/%Y")}</span>'
                f'</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("Nenhum gasto cadastrado.")


def pagina_cadastrar():
    st.markdown('<div class="page-title">➕ Cadastrar Gasto</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Registre um novo gasto</div>', unsafe_allow_html=True)

    tipos_existentes = sorted(set(
        [g.tipo for g in get_gastos()] + TIPOS_PADRAO
    ))

    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            usar_tipo_custom = st.checkbox("Digitar tipo manualmente")
            if usar_tipo_custom:
                tipo = st.text_input("Tipo de Gasto", placeholder="Ex: Viagem")
            else:
                tipo = st.selectbox("Tipo de Gasto", tipos_existentes)

            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")

        with col2:
            data_gasto = st.date_input("Data do Gasto", value=date.today(), max_value=date.today())
            forma = st.selectbox("Forma de Pagamento", [f.value for f in FormaPagamento])

        submitted = st.form_submit_button("💾 Salvar Gasto", use_container_width=True)

    if submitted:
        erros = validar_gasto(tipo, data_gasto, str(valor), forma)
        if erros:
            for e in erros:
                st.error(e)
        else:
            novo = Gasto(
                tipo=tipo.strip(),
                data=data_gasto,
                valor=float(valor),
                forma=FormaPagamento(forma),
            )
            save_gasto(novo)
            st.success(f"✅ Gasto de **R$ {valor:,.2f}** em **{tipo}** cadastrado com sucesso!")
            st.balloons()


def pagina_listar():
    st.markdown('<div class="page-title">📋 Listar Gastos</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visualize, edite ou exclua seus registros</div>', unsafe_allow_html=True)

    gastos = get_gastos()
    if not gastos:
        st.info("Nenhum gasto cadastrado ainda.")
        return

    # Filtros
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            tipos_disp = ["Todos"] + sorted(set(g.tipo for g in gastos))
            filtro_tipo = st.selectbox("Tipo", tipos_disp)
        with col2:
            formas_disp = ["Todos"] + [f.value for f in FormaPagamento]
            filtro_forma = st.selectbox("Forma de Pagamento", formas_disp)
        with col3:
            filtro_texto = st.text_input("Buscar por tipo", placeholder="Digite para filtrar...")

    gastos_filtrados = gastos
    if filtro_tipo != "Todos":
        gastos_filtrados = [g for g in gastos_filtrados if g.tipo == filtro_tipo]
    if filtro_forma != "Todos":
        gastos_filtrados = [g for g in gastos_filtrados if g.forma.value == filtro_forma]
    if filtro_texto:
        gastos_filtrados = [g for g in gastos_filtrados if filtro_texto.lower() in g.tipo.lower()]

    gastos_filtrados = sorted(gastos_filtrados, key=lambda g: g.data, reverse=True)

    st.markdown(f"**{len(gastos_filtrados)}** registro(s) encontrado(s) · "
                f"Total: **R$ {sum(g.valor for g in gastos_filtrados):,.2f}**")
    st.markdown("---")

    if "editando_id" not in st.session_state:
        st.session_state.editando_id = None
    if "confirmando_delete" not in st.session_state:
        st.session_state.confirmando_delete = None

    for g in gastos_filtrados:
        with st.container():
            if st.session_state.editando_id == g.id:
                # Formulário de edição inline
                st.markdown(f'<div class="gasto-card">', unsafe_allow_html=True)
                st.markdown(f"**Editando gasto:** {g.tipo} — {g.data.strftime('%d/%m/%Y')}")
                tipos_existentes = sorted(set([gx.tipo for gx in get_gastos()] + TIPOS_PADRAO))
                with st.form(f"edit_{g.id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        novo_tipo = st.selectbox("Tipo", tipos_existentes,
                                                 index=tipos_existentes.index(g.tipo) if g.tipo in tipos_existentes else 0,
                                                 key=f"tipo_{g.id}")
                        novo_valor = st.number_input("Valor (R$)", value=g.valor, min_value=0.01,
                                                     step=0.01, format="%.2f", key=f"valor_{g.id}")
                    with c2:
                        nova_data = st.date_input("Data", value=g.data, key=f"data_{g.id}")
                        nova_forma = st.selectbox("Forma", [f.value for f in FormaPagamento],
                                                  index=[f.value for f in FormaPagamento].index(g.forma.value),
                                                  key=f"forma_{g.id}")
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        salvar = st.form_submit_button("✅ Salvar", use_container_width=True)
                    with bc2:
                        cancelar = st.form_submit_button("✖ Cancelar", use_container_width=True)

                if salvar:
                    erros = validar_gasto(novo_tipo, nova_data, str(novo_valor), nova_forma)
                    if erros:
                        for e in erros:
                            st.error(e)
                    else:
                        update_gasto(g.id, novo_tipo, nova_data, float(novo_valor), FormaPagamento(nova_forma))
                        st.session_state.editando_id = None
                        st.success("Gasto atualizado!")
                        st.rerun()
                if cancelar:
                    st.session_state.editando_id = None
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                col_info, col_acoes = st.columns([4, 1])
                with col_info:
                    st.markdown(
                        f'<div class="gasto-card" style="display:flex;justify-content:space-between;align-items:center">'
                        f'<div>'
                        f'<span style="font-family:Syne,sans-serif;font-weight:700;font-size:1rem">{g.tipo}</span>'
                        f'&nbsp;<span class="badge">{g.forma.value}</span>'
                        f'<br><span style="color:#555;font-size:0.82rem">{g.data.strftime("%d/%m/%Y")} &nbsp;·&nbsp; ID: {g.id[:8]}…</span>'
                        f'</div>'
                        f'<span style="color:#f0c060;font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem">R$ {g.valor:,.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_acoes:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✏️", key=f"edit_btn_{g.id}", help="Editar"):
                        st.session_state.editando_id = g.id
                        st.session_state.confirmando_delete = None
                        st.rerun()
                    if st.session_state.confirmando_delete == g.id:
                        if st.button("⚠️ Confirmar", key=f"confirm_{g.id}"):
                            delete_gasto(g.id)
                            st.session_state.confirmando_delete = None
                            st.success("Gasto excluído.")
                            st.rerun()
                        if st.button("Cancelar", key=f"cancel_del_{g.id}"):
                            st.session_state.confirmando_delete = None
                            st.rerun()
                    else:
                        if st.button("🗑️", key=f"del_btn_{g.id}", help="Excluir"):
                            st.session_state.confirmando_delete = g.id
                            st.session_state.editando_id = None
                            st.rerun()


def pagina_relatorio():
    st.markdown('<div class="page-title">📈 Relatório por Período</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Análise detalhada dos gastos em um período definido</div>', unsafe_allow_html=True)

    gastos = get_gastos()

    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data de Início", value=date.today().replace(day=1))
    with col2:
        data_fim = st.date_input("Data de Fim", value=date.today())

    if data_inicio > data_fim:
        st.error("A data de início não pode ser posterior à data de fim.")
        return

    periodo = Periodo.new(data_inicio, data_fim)
    relatorio = RelatorioGastos(periodo, gastos)
    lista = relatorio.listarGastosNoPeriodo()

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total no Período", f"R$ {relatorio.totalMensal():,.2f}")
    with col2:
        st.metric("Quantidade de Gastos", len(lista))
    with col3:
        media = relatorio.totalMensal() / max(len(lista), 1)
        st.metric("Média por Gasto", f"R$ {media:,.2f}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Lista Completa", "📦 Por Tipo", "💳 Por Forma de Pagamento"])

    with tab1:
        if lista:
            dados = [
                {
                    "Data": g.data.strftime("%d/%m/%Y"),
                    "Tipo": g.tipo,
                    "Valor (R$)": f"{g.valor:,.2f}",
                    "Forma": g.forma.value,
                }
                for g in lista
            ]
            st.dataframe(dados, use_container_width=True, hide_index=True)

            csv_content = relatorio.exportarCSV()
            st.download_button(
                label="⬇️ Exportar CSV",
                data=csv_content.encode("utf-8"),
                file_name=f"gastos_{data_inicio}_{data_fim}.csv",
                mime="text/csv",
                use_container_width=False,
            )
        else:
            st.info("Nenhum gasto encontrado neste período.")

    with tab2:
        por_tipo = relatorio.agruparPorTipo()
        if por_tipo:
            total = sum(por_tipo.values())
            for tipo, val in por_tipo.items():
                pct = val / total * 100
                st.markdown(
                    f'<div class="gasto-card" style="display:flex;justify-content:space-between;align-items:center">'
                    f'<div><span style="font-family:Syne,sans-serif;font-weight:700">{tipo}</span>'
                    f'<br><div style="background:#2a2a35;border-radius:4px;height:4px;width:200px;margin-top:6px">'
                    f'<div style="background:#f0c060;border-radius:4px;height:4px;width:{pct*2}px"></div></div></div>'
                    f'<div style="text-align:right">'
                    f'<span class="badge badge-gold">{pct:.1f}%</span><br>'
                    f'<span style="color:#f0c060;font-family:Syne,sans-serif;font-weight:800">R$ {val:,.2f}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Nenhum dado disponível.")

    with tab3:
        por_forma = relatorio.agruparPorFormaPagamento()
        if por_forma:
            total = sum(por_forma.values())
            for forma, val in por_forma.items():
                pct = val / total * 100
                st.markdown(
                    f'<div class="gasto-card" style="display:flex;justify-content:space-between;align-items:center">'
                    f'<div><span style="font-family:Syne,sans-serif;font-weight:700">{forma}</span>'
                    f'<br><div style="background:#2a2a35;border-radius:4px;height:4px;width:200px;margin-top:6px">'
                    f'<div style="background:#f0c060;border-radius:4px;height:4px;width:{pct*2}px"></div></div></div>'
                    f'<div style="text-align:right">'
                    f'<span class="badge badge-gold">{pct:.1f}%</span><br>'
                    f'<span style="color:#f0c060;font-family:Syne,sans-serif;font-weight:800">R$ {val:,.2f}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Nenhum dado disponível.")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    configurar_pagina()
    init_storage()

    with st.sidebar:
        st.markdown(
            '<div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;'
            'color:#f0c060;margin-bottom:0.2rem">💳 Gastos</div>'
            '<div style="color:#444;font-size:0.75rem;margin-bottom:1.5rem">Controle Financeiro Pessoal</div>',
            unsafe_allow_html=True
        )

        pagina = st.radio(
            "Navegação",
            ["Dashboard", "Cadastrar", "Listar", "Relatório"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        total_gastos = len(get_gastos())
        total_valor = sum(g.valor for g in get_gastos())
        st.markdown(
            f'<div style="color:#555;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.07em">Registros</div>'
            f'<div style="font-family:Syne,sans-serif;font-weight:700;color:#e8e4dc;font-size:1.1rem">{total_gastos}</div>'
            f'<br>'
            f'<div style="color:#555;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.07em">Total Geral</div>'
            f'<div style="font-family:Syne,sans-serif;font-weight:700;color:#f0c060;font-size:1.1rem">R$ {total_valor:,.2f}</div>',
            unsafe_allow_html=True
        )

    if pagina == "Dashboard":
        pagina_dashboard()
    elif pagina == "Cadastrar":
        pagina_cadastrar()
    elif pagina == "Listar":
        pagina_listar()
    elif pagina == "Relatório":
        pagina_relatorio()


if __name__ == "__main__":
    main()