"""
Sistema de Comandas - app.py
Execute com: streamlit run app.py
"""

import streamlit as st
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

# ─────────────────────────────────────────────
#  DOMAIN LAYER
# ─────────────────────────────────────────────

class Produto:
    def __init__(self, codigo: int, nome: str, valor_unitario: float):
        if valor_unitario <= 0:
            raise ValueError("Valor unitário deve ser maior que zero.")
        self.codigo = codigo
        self.nome = nome
        self.valor_unitario = float(valor_unitario)

    def atualizar_valor(self, novo_valor: float) -> None:
        if novo_valor <= 0:
            raise ValueError("Valor unitário deve ser maior que zero.")
        self.valor_unitario = float(novo_valor)

    def to_dict(self):
        return {"codigo": self.codigo, "nome": self.nome, "valor_unitario": self.valor_unitario}

    @staticmethod
    def from_dict(d):
        return Produto(d["codigo"], d["nome"], d["valor_unitario"])


class ItemComanda:
    def __init__(self, produto: Produto, quantidade: int):
        if quantidade < 1:
            raise ValueError("Quantidade deve ser >= 1.")
        self._produto = produto
        self.quantidade = quantidade
        self.preco_unit_lancamento = produto.valor_unitario  # snapshot at launch

    @property
    def produto(self) -> Produto:
        return self._produto

    @property
    def subtotal(self) -> float:
        return round(self.preco_unit_lancamento * self.quantidade, 2)

    def calcular_subtotal(self) -> float:
        return self.subtotal

    def to_dict(self):
        return {
            "produto": self._produto.to_dict(),
            "quantidade": self.quantidade,
            "preco_unit_lancamento": self.preco_unit_lancamento,
        }

    @staticmethod
    def from_dict(d):
        p = Produto.from_dict(d["produto"])
        item = ItemComanda.__new__(ItemComanda)
        item._produto = p
        item.quantidade = d["quantidade"]
        item.preco_unit_lancamento = d["preco_unit_lancamento"]
        return item


class Comanda:
    def __init__(self, numero: int):
        self.numero = numero
        self.status = "aberta"          # "aberta" | "finalizada"
        self._itens: list[ItemComanda] = []

    # ── derived ──────────────────────────────
    @property
    def itens(self) -> list[ItemComanda]:
        return list(self._itens)

    @property
    def valor_total(self) -> float:
        return round(sum(i.subtotal for i in self._itens), 2)

    # ── methods ──────────────────────────────
    def abrir(self) -> None:
        self.status = "aberta"

    def registrar_consumo(self, produto: Produto, quantidade: int) -> None:
        if self.status == "finalizada":
            raise PermissionError("Comanda finalizada. Não é possível lançar novos produtos. (RF07)")
        if quantidade < 1:
            raise ValueError("Quantidade deve ser >= 1.")
        self._itens.append(ItemComanda(produto, quantidade))

    def listar_itens(self) -> list[ItemComanda]:
        return self.itens

    def calcular_total(self) -> float:
        return self.valor_total

    def finalizar(self) -> None:
        self.status = "finalizada"

    def to_dict(self):
        return {
            "numero": self.numero,
            "status": self.status,
            "itens": [i.to_dict() for i in self._itens],
        }

    @staticmethod
    def from_dict(d):
        c = Comanda.__new__(Comanda)
        c.numero = d["numero"]
        c.status = d["status"]
        c._itens = [ItemComanda.from_dict(i) for i in d.get("itens", [])]
        return c


# ─────────────────────────────────────────────
#  PERSISTENCE (st.session_state as in-memory DB)
# ─────────────────────────────────────────────

def _init_state():
    if "produtos" not in st.session_state:
        st.session_state.produtos: dict[int, Produto] = {}
    if "comandas" not in st.session_state:
        st.session_state.comandas: dict[int, Comanda] = {}
    if "_next_codigo" not in st.session_state:
        st.session_state._next_codigo = 1
    if "_next_comanda" not in st.session_state:
        st.session_state._next_comanda = 1
    if "_seeded" not in st.session_state:
        _seed_mock_data()
        st.session_state._seeded = True


def _seed_mock_data():
    produtos_mock = [
        (1, "Água Mineral 500ml", 4.00),
        (2, "Refrigerante Lata", 7.00),
        (3, "Suco Natural 300ml", 9.50),
        (4, "Cerveja Long Neck", 12.00),
        (5, "Coxinha", 6.00),
        (6, "Pão de Queijo", 5.00),
        (7, "Porção de Batata Frita", 28.00),
        (8, "Hambúrguer Artesanal", 35.00),
    ]
    for cod, nome, valor in produtos_mock:
        p = Produto(cod, nome, valor)
        st.session_state.produtos[cod] = p
    st.session_state._next_codigo = 9

    # Mock comanda já aberta
    c1 = Comanda(1)
    c1.registrar_consumo(st.session_state.produtos[2], 2)
    c1.registrar_consumo(st.session_state.produtos[7], 1)
    st.session_state.comandas[1] = c1

    # Mock comanda finalizada
    c2 = Comanda(2)
    c2.registrar_consumo(st.session_state.produtos[4], 4)
    c2.registrar_consumo(st.session_state.produtos[6], 3)
    c2.finalizar()
    st.session_state.comandas[2] = c2

    st.session_state._next_comanda = 3


def next_codigo() -> int:
    cod = st.session_state._next_codigo
    st.session_state._next_codigo += 1
    return cod


def next_numero_comanda() -> int:
    n = st.session_state._next_comanda
    st.session_state._next_comanda += 1
    return n


# ─────────────────────────────────────────────
#  HELPERS / UI UTILITIES
# ─────────────────────────────────────────────

def badge_status(status: str) -> str:
    if status == "aberta":
        return "🟢 Aberta"
    return "🔴 Finalizada"


def fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ─────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────

def page_dashboard():
    st.title("📊 Dashboard")

    produtos = st.session_state.produtos
    comandas = st.session_state.comandas

    abertas = [c for c in comandas.values() if c.status == "aberta"]
    finalizadas = [c for c in comandas.values() if c.status == "finalizada"]
    total_aberto = sum(c.valor_total for c in abertas)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Produtos Cadastrados", len(produtos))
    col2.metric("Comandas Abertas", len(abertas))
    col3.metric("Comandas Finalizadas", len(finalizadas))
    col4.metric("Total em Aberto", fmt_brl(total_aberto))

    st.divider()
    st.subheader("Comandas Abertas")
    if abertas:
        for c in sorted(abertas, key=lambda x: x.numero):
            with st.expander(f"Comanda #{c.numero} — {fmt_brl(c.valor_total)}"):
                if c.itens:
                    rows = [{"Produto": i.produto.nome,
                             "Qtd": i.quantidade,
                             "Preço Unit.": fmt_brl(i.preco_unit_lancamento),
                             "Subtotal": fmt_brl(i.subtotal)} for i in c.itens]
                    st.table(rows)
                else:
                    st.info("Sem itens lançados.")
    else:
        st.info("Nenhuma comanda aberta no momento.")


def page_produtos():
    st.title("🛍️ Produtos")
    produtos = st.session_state.produtos

    tab1, tab2 = st.tabs(["Listar Produtos", "Cadastrar Produto"])

    with tab1:
        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            rows = [{"Código": p.codigo, "Nome": p.nome, "Valor Unitário": fmt_brl(p.valor_unitario)}
                    for p in sorted(produtos.values(), key=lambda x: x.codigo)]
            st.dataframe(rows, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Atualizar Valor Unitário")
        if produtos:
            opcoes = {f"[{p.codigo}] {p.nome}": p.codigo for p in produtos.values()}
            sel = st.selectbox("Produto", list(opcoes.keys()), key="upd_sel")
            cod_sel = opcoes[sel]
            novo_val = st.number_input("Novo valor unitário (R$)", min_value=0.01, step=0.50,
                                       value=produtos[cod_sel].valor_unitario, format="%.2f", key="upd_val")
            if st.button("Atualizar Valor", key="btn_upd"):
                try:
                    produtos[cod_sel].atualizar_valor(novo_val)
                    st.success(f"Valor atualizado para {fmt_brl(novo_val)}.")
                except ValueError as e:
                    st.error(str(e))

    with tab2:
        with st.form("form_produto"):
            nome = st.text_input("Nome do Produto")
            valor = st.number_input("Valor Unitário (R$)", min_value=0.01, step=0.50, format="%.2f")
            submitted = st.form_submit_button("Cadastrar")
        if submitted:
            nome = nome.strip()
            if not nome:
                st.error("Nome não pode ser vazio.")
            elif valor <= 0:
                st.error("Valor unitário deve ser maior que zero. (RNF02)")
            else:
                cod = next_codigo()
                p = Produto(cod, nome, valor)
                st.session_state.produtos[cod] = p
                st.success(f"Produto '{nome}' cadastrado com código #{cod}.")


def page_comandas():
    st.title("🗒️ Comandas")
    comandas = st.session_state.comandas
    produtos = st.session_state.produtos

    tab1, tab2, tab3 = st.tabs(["Listar Comandas", "Abrir Comanda", "Registrar Consumo"])

    # ── tab: Listar ────────────────────────────
    with tab1:
        if not comandas:
            st.info("Nenhuma comanda cadastrada.")
        else:
            for c in sorted(comandas.values(), key=lambda x: x.numero):
                status_icon = "🟢" if c.status == "aberta" else "🔴"
                with st.expander(f"{status_icon} Comanda #{c.numero} — {badge_status(c.status)} — {fmt_brl(c.valor_total)}"):
                    if c.itens:
                        rows = [{"Produto": i.produto.nome,
                                 "Qtd": i.quantidade,
                                 "Preço Unit.": fmt_brl(i.preco_unit_lancamento),
                                 "Subtotal": fmt_brl(i.subtotal)} for i in c.itens]
                        st.table(rows)
                        st.markdown(f"**Total: {fmt_brl(c.valor_total)}**")
                    else:
                        st.info("Sem itens lançados.")

                    if c.status == "aberta":
                        if st.button(f"✅ Finalizar Comanda #{c.numero}", key=f"fin_{c.numero}"):
                            c.finalizar()
                            st.success(f"Comanda #{c.numero} finalizada!")
                            st.rerun()

    # ── tab: Abrir ─────────────────────────────
    with tab2:
        st.subheader("Abrir Nova Comanda")
        proximo = st.session_state._next_comanda
        st.info(f"A próxima comanda será a **#{proximo}** (gerada automaticamente em ordem crescente — RNF03).")
        if st.button("Abrir Comanda", type="primary"):
            num = next_numero_comanda()
            c = Comanda(num)
            c.abrir()
            comandas[num] = c
            st.success(f"Comanda #{num} aberta com sucesso!")

    # ── tab: Registrar Consumo ──────────────────
    with tab3:
        st.subheader("Registrar Consumo em Comanda")
        abertas = {f"Comanda #{c.numero}": c.numero for c in comandas.values() if c.status == "aberta"}
        if not abertas:
            st.warning("Não há comandas abertas. Abra uma comanda primeiro.")
        elif not produtos:
            st.warning("Não há produtos cadastrados.")
        else:
            with st.form("form_consumo"):
                comanda_sel = st.selectbox("Comanda", list(abertas.keys()))
                prod_opts = {f"[{p.codigo}] {p.nome} — {fmt_brl(p.valor_unitario)}": p.codigo
                             for p in sorted(produtos.values(), key=lambda x: x.codigo)}
                prod_sel = st.selectbox("Produto", list(prod_opts.keys()))
                quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
                submitted = st.form_submit_button("Registrar")

            if submitted:
                num = abertas[comanda_sel]
                cod = prod_opts[prod_sel]
                try:
                    comandas[num].registrar_consumo(produtos[cod], int(quantidade))
                    item_adicionado = comandas[num].itens[-1]
                    st.success(
                        f"{quantidade}x {produtos[cod].nome} adicionado(s) à Comanda #{num}. "
                        f"Subtotal: {fmt_brl(item_adicionado.subtotal)}"
                    )
                except (PermissionError, ValueError) as e:
                    st.error(str(e))


def page_finalizar():
    st.title("✅ Finalizar Comanda")
    comandas = st.session_state.comandas
    abertas = [c for c in comandas.values() if c.status == "aberta"]

    if not abertas:
        st.info("Não há comandas abertas para finalizar.")
        return

    opcoes = {f"Comanda #{c.numero} — {fmt_brl(c.valor_total)}": c.numero for c in sorted(abertas, key=lambda x: x.numero)}
    sel = st.selectbox("Selecione a comanda", list(opcoes.keys()))
    num = opcoes[sel]
    c = comandas[num]

    st.subheader(f"Resumo — Comanda #{c.numero}")
    if c.itens:
        rows = [{"Produto": i.produto.nome,
                 "Qtd": i.quantidade,
                 "Preço Unit.": fmt_brl(i.preco_unit_lancamento),
                 "Subtotal": fmt_brl(i.subtotal)} for i in c.itens]
        st.table(rows)
        st.markdown(f"### 💰 Total: {fmt_brl(c.valor_total)}")
    else:
        st.warning("Comanda sem itens.")

    st.divider()
    confirmar = st.checkbox("Confirmo o fechamento desta comanda")
    if st.button("Finalizar Comanda", type="primary", disabled=not confirmar):
        c.finalizar()
        st.success(f"Comanda #{c.numero} finalizada! Novos lançamentos estão bloqueados. (RF07)")
        st.balloons()
        st.rerun()


# ─────────────────────────────────────────────
#  APP ENTRY POINT
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Sistema de Comandas",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS — dark, industrial/utilitarian aesthetic
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stApp {
        background: #0f0f0f;
        color: #e8e6e0;
    }
    [data-testid="stSidebar"] {
        background: #161616;
        border-right: 1px solid #2a2a2a;
    }
    [data-testid="stSidebar"] * {
        color: #e8e6e0 !important;
    }
    .stButton > button {
        background: #d4a843;
        color: #0f0f0f;
        border: none;
        border-radius: 2px;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: #e8bf6a;
        color: #0f0f0f;
    }
    .stButton > button[kind="primary"] {
        background: #d4a843;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #888;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #d4a843 !important;
        border-bottom: 2px solid #d4a843 !important;
    }
    div[data-testid="metric-container"] {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 2px;
        padding: 1rem;
    }
    .stDataFrame, .stTable {
        background: #1a1a1a !important;
    }
    .stExpander {
        background: #1a1a1a;
        border: 1px solid #2a2a2a !important;
        border-radius: 2px;
    }
    .stSelectbox label, .stNumberInput label, .stTextInput label, .stCheckbox label {
        color: #aaa !important;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    h1 { font-size: 1.8rem; font-weight: 800; color: #d4a843; letter-spacing: -0.02em; }
    h2, h3 { color: #e8e6e0; }
    hr { border-color: #2a2a2a !important; }
    </style>
    """, unsafe_allow_html=True)

    _init_state()

    st.sidebar.markdown("## 🍽️ Comandas")
    st.sidebar.markdown("---")

    paginas = {
        "📊 Dashboard": page_dashboard,
        "🛍️ Produtos": page_produtos,
        "🗒️ Comandas": page_comandas,
        "✅ Finalizar": page_finalizar,
    }

    sel = st.sidebar.radio("Navegação", list(paginas.keys()), label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"**Produtos:** {len(st.session_state.produtos)}  \n"
        f"**Comandas:** {len(st.session_state.comandas)}"
    )

    paginas[sel]()


if __name__ == "__main__":
    main()