import streamlit as st
import pandas as pd
from datetime import date, datetime
import json

# ─────────────────────────────────────────────
# Modelo de dados – espelha o diagrama de classes
# ─────────────────────────────────────────────

class ContaDeLuz:
    def __init__(
        self,
        data_leitura: date,
        numero_leitura: int,
        kw_gasto: float,
        valor_pagar: float,
        data_pagamento: date,
    ):
        self.data_leitura = data_leitura
        self.numero_leitura = numero_leitura
        self.kw_gasto = kw_gasto
        self.valor_pagar = valor_pagar
        self.data_pagamento = data_pagamento
        self.media_consumo: float = 0.0  # calculada pelo sistema

    def obter_mes_referencia(self) -> str:
        return self.data_leitura.strftime("%B/%Y")

    def obter_consumo(self) -> float:
        return self.kw_gasto

    def to_dict(self) -> dict:
        return {
            "data_leitura": self.data_leitura.isoformat(),
            "numero_leitura": self.numero_leitura,
            "kw_gasto": self.kw_gasto,
            "valor_pagar": self.valor_pagar,
            "data_pagamento": self.data_pagamento.isoformat(),
            "media_consumo": self.media_consumo,
        }


class SistemasContas:
    def __init__(self):
        self.contas: list[ContaDeLuz] = []

    def adicionar_conta(self, conta: ContaDeLuz) -> None:
        self.contas.append(conta)
        self._recalcular_medias()

    def _recalcular_medias(self):
        if not self.contas:
            return
        media = sum(c.kw_gasto for c in self.contas) / len(self.contas)
        for c in self.contas:
            c.media_consumo = media

    def obter_mes_maior_consumo(self) -> ContaDeLuz | None:
        if not self.contas:
            return None
        return max(self.contas, key=lambda c: c.kw_gasto)

    def obter_mes_menor_consumo(self) -> ContaDeLuz | None:
        if not self.contas:
            return None
        return min(self.contas, key=lambda c: c.kw_gasto)

    def media_geral(self) -> float:
        if not self.contas:
            return 0.0
        return sum(c.kw_gasto for c in self.contas) / len(self.contas)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.contas:
            return pd.DataFrame()
        rows = []
        maior = self.obter_mes_maior_consumo()
        menor = self.obter_mes_menor_consumo()
        for c in self.contas:
            rows.append(
                {
                    "Mês Referência": c.obter_mes_referencia(),
                    "Nº Leitura": c.numero_leitura,
                    "Data Leitura": c.data_leitura.strftime("%d/%m/%Y"),
                    "kWh Gasto": c.kw_gasto,
                    "Valor a Pagar (R$)": c.valor_pagar,
                    "Data Pagamento": c.data_pagamento.strftime("%d/%m/%Y"),
                    "Média Consumo (kWh)": round(c.media_consumo, 2),
                    "_maior": c is maior,
                    "_menor": c is menor,
                }
            )
        return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Persistência leve via session_state
# ─────────────────────────────────────────────

def get_sistema() -> SistemasContas:
    if "sistema" not in st.session_state:
        st.session_state["sistema"] = SistemasContas()
    return st.session_state["sistema"]


# ─────────────────────────────────────────────
# Estilos visuais
# ─────────────────────────────────────────────

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Mono', monospace;
        }

        /* Fundo geral */
        .stApp {
            background: #0d0f14;
            color: #e8e4d9;
        }

        /* Cabeçalho principal */
        .hero {
            background: linear-gradient(135deg, #1a1f2e 0%, #0d0f14 60%);
            border: 1px solid #2a3044;
            border-radius: 16px;
            padding: 2.5rem 2rem 2rem 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        .hero::before {
            content: '';
            position: absolute;
            top: -60px; right: -60px;
            width: 200px; height: 200px;
            background: radial-gradient(circle, #f5c518 0%, transparent 70%);
            opacity: 0.08;
            border-radius: 50%;
        }
        .hero h1 {
            font-family: 'Syne', sans-serif;
            font-size: 2.4rem;
            font-weight: 800;
            color: #f5c518;
            margin: 0 0 .3rem 0;
            letter-spacing: -1px;
        }
        .hero p {
            color: #7a8099;
            margin: 0;
            font-size: .85rem;
        }

        /* Cards de métricas */
        .metric-card {
            background: #141720;
            border: 1px solid #252a3a;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            text-align: center;
        }
        .metric-card.highlight-max {
            border-color: #e05c3a;
            background: linear-gradient(135deg, #1e1410, #141720);
        }
        .metric-card.highlight-min {
            border-color: #3ae0a0;
            background: linear-gradient(135deg, #0d1a14, #141720);
        }
        .metric-label {
            font-size: .7rem;
            color: #5a617a;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: .5rem;
        }
        .metric-value {
            font-family: 'Syne', sans-serif;
            font-size: 1.9rem;
            font-weight: 800;
            color: #e8e4d9;
        }
        .metric-sub {
            font-size: .75rem;
            color: #7a8099;
            margin-top: .2rem;
        }
        .badge-max { color: #e05c3a; }
        .badge-min { color: #3ae0a0; }

        /* Tabela */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }

        /* Formulário */
        .form-box {
            background: #141720;
            border: 1px solid #252a3a;
            border-radius: 14px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
        }
        .form-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #f5c518;
            margin-bottom: 1.2rem;
            letter-spacing: -.3px;
        }

        /* Botão principal */
        div.stButton > button {
            background: #f5c518;
            color: #0d0f14;
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: .9rem;
            border: none;
            border-radius: 8px;
            padding: .65rem 1.8rem;
            cursor: pointer;
            transition: background .2s;
            width: 100%;
        }
        div.stButton > button:hover {
            background: #ffd740;
        }

        /* Inputs */
        input, textarea, select {
            background: #0d0f14 !important;
            border: 1px solid #2a3044 !important;
            color: #e8e4d9 !important;
            border-radius: 8px !important;
        }

        /* Seção título */
        .section-title {
            font-family: 'Syne', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: #e8e4d9;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 1.8rem 0 1rem 0;
            padding-bottom: .5rem;
            border-bottom: 1px solid #1e2234;
        }

        /* Alerta vazio */
        .empty-state {
            text-align: center;
            color: #3a4060;
            font-size: .9rem;
            padding: 3rem;
            border: 1px dashed #1e2234;
            border-radius: 12px;
        }

        /* Toast de sucesso */
        .stSuccess {
            background: #0d1a14 !important;
            border: 1px solid #3ae0a0 !important;
            color: #3ae0a0 !important;
            border-radius: 8px !important;
        }
        .stError {
            background: #1a0d0d !important;
            border: 1px solid #e05c3a !important;
            color: #e05c3a !important;
            border-radius: 8px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Componentes reutilizáveis
# ─────────────────────────────────────────────

def render_metric(label: str, value: str, sub: str = "", css_class: str = ""):
    st.markdown(
        f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {'<div class="metric-sub">' + sub + '</div>' if sub else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Layout principal
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="ContaLuz — Sistema de Contas de Energia",
        page_icon="⚡",
        layout="wide",
    )
    inject_css()

    sistema = get_sistema()

    # ── Hero ──────────────────────────────────
    st.markdown(
        """
        <div class="hero">
            <h1>⚡ ContaLuz</h1>
            <p>Sistema de gerenciamento e análise de contas de energia elétrica</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Layout 2 colunas: formulário | painel ──
    col_form, col_painel = st.columns([1, 2], gap="large")

    # ─── FORMULÁRIO ───────────────────────────
    with col_form:
        st.markdown('<div class="form-title">📋 Registrar Nova Conta</div>', unsafe_allow_html=True)

        with st.form("form_conta", clear_on_submit=True):
            data_leitura = st.date_input("Data da Leitura", value=date.today())
            numero_leitura = st.number_input(
                "Número da Leitura", min_value=0, step=1, value=0
            )
            kw_gasto = st.number_input(
                "kWh Gasto", min_value=0.0, step=0.1, format="%.2f"
            )
            valor_pagar = st.number_input(
                "Valor a Pagar (R$)", min_value=0.0, step=0.01, format="%.2f"
            )
            data_pagamento = st.date_input("Data de Pagamento", value=date.today())

            submitted = st.form_submit_button("➕ Adicionar Conta")

        if submitted:
            # RNF04 – valores negativos
            if kw_gasto < 0 or valor_pagar < 0:
                st.error("❌ Valores negativos não são permitidos.")
            else:
                nova_conta = ContaDeLuz(
                    data_leitura=data_leitura,
                    numero_leitura=int(numero_leitura),
                    kw_gasto=kw_gasto,
                    valor_pagar=valor_pagar,
                    data_pagamento=data_pagamento,
                )
                sistema.adicionar_conta(nova_conta)
                st.success(f"✅ Conta de {nova_conta.obter_mes_referencia()} registrada!")
                st.rerun()

    # ─── PAINEL DIREITO ───────────────────────
    with col_painel:

        total = len(sistema.contas)
        maior = sistema.obter_mes_maior_consumo()
        menor = sistema.obter_mes_menor_consumo()
        media = sistema.media_geral()

        # ── Métricas ──
        st.markdown('<div class="section-title">Resumo</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            render_metric("Total de Contas", str(total))
        with m2:
            render_metric(
                "Média de Consumo",
                f"{media:.1f}",
                sub="kWh",
            )
        with m3:
            render_metric(
                "🔴 Maior Consumo",
                f"{maior.kw_gasto:.1f}" if maior else "—",
                sub=maior.obter_mes_referencia() if maior else "",
                css_class="highlight-max",
            )
        with m4:
            render_metric(
                "🟢 Menor Consumo",
                f"{menor.kw_gasto:.1f}" if menor else "—",
                sub=menor.obter_mes_referencia() if menor else "",
                css_class="highlight-min",
            )

        # ── Histórico ──
        st.markdown('<div class="section-title">Histórico de Contas</div>', unsafe_allow_html=True)

        if total == 0:
            st.markdown(
                '<div class="empty-state">Nenhuma conta registrada ainda.<br>Use o formulário ao lado para começar.</div>',
                unsafe_allow_html=True,
            )
        else:
            df = sistema.to_dataframe()

            # Estilo condicional: destaca maior (vermelho) e menor (verde)
            def highlight_row(row):
                if row["_maior"]:
                    return ["background-color: #2a1510; color: #e05c3a"] * len(row)
                if row["_menor"]:
                    return ["background-color: #0d1a12; color: #3ae0a0"] * len(row)
                return [""] * len(row)

            df_display = df.drop(columns=["_maior", "_menor"])
            styled = df_display.style.apply(
                lambda row: highlight_row(df.loc[row.name]),
                axis=1,
            ).format(
                {
                    "kWh Gasto": "{:.2f}",
                    "Valor a Pagar (R$)": "R$ {:.2f}",
                    "Média Consumo (kWh)": "{:.2f}",
                }
            )
            st.dataframe(styled, use_container_width=True, hide_index=True)

            # ── Gráfico de consumo ──
            st.markdown('<div class="section-title">Evolução do Consumo (kWh)</div>', unsafe_allow_html=True)

            chart_df = df_display[["Mês Referência", "kWh Gasto"]].copy()
            chart_df = chart_df.rename(columns={"Mês Referência": "index"}).set_index("index")
            st.line_chart(chart_df, color="#f5c518")

            # ── Exportar ──
            csv = df_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Exportar CSV",
                data=csv,
                file_name="historico_contaluz.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()