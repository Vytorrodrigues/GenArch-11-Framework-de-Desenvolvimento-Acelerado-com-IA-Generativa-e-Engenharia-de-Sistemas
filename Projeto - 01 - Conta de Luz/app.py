import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================================================
# MODELAGEM DE CLASSES (Baseado no Diagrama UML)
# =====================================================================

class ContaDeLuz:
    def __init__(self, datasLeitura, numeroLeitura, kwGasto, valoPagar, dataPagamento, mediaConsumo):
        self.datasLeitura = datasLeitura
        self.numeroLeitura = numeroLeitura
        self.kwGasto = kwGasto
        self.valoPagar = valoPagar # Mantido como no diagrama (valoPagar)
        self.dataPagamento = dataPagamento
        self.mediaConsumo = mediaConsumo

    def obterMesReferencia(self):
        """Retorna o mês/ano no formato exigido pela planilha (ex: jul/05)"""
        meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
        mes = meses[self.datasLeitura.month - 1]
        ano = str(self.datasLeitura.year)[-2:]
        return f"{mes}/{ano}"

    def obterConsumo(self):
        return self.kwGasto

class SistemasContas:
    def __init__(self):
        # Relacionamento 1 para 0..* com ContaDeLuz
        self.contas = []

    def adicionarConta(self, conta: ContaDeLuz):
        self.contas.append(conta)

    def obterMesMaiorConsumo(self):
        if not self.contas:
            return None
        # Utiliza a função obterConsumo() para encontrar o valor máximo
        return max(self.contas, key=lambda c: c.obterConsumo())

    def obterMesMenorConsumo(self):
        if not self.contas:
            return None
        # Utiliza a função obterConsumo() para encontrar o valor mínimo
        return min(self.contas, key=lambda c: c.obterConsumo())

    def realizarMediaConsumos(self):
        """Método adicional para atender ao RF05 (Realizar média dos consumos)"""
        if not self.contas:
            return 0.0
        total = sum(c.obterConsumo() for c in self.contas)
        return total / len(self.contas)


# =====================================================================
# INTERFACE COM STREAMLIT (Atendendo aos RNFs)
# =====================================================================

# RNF01: Interface simples e intuitiva
st.set_page_config(page_title="Controle de Conta de Luz", page_icon="⚡", layout="wide")

# RF04: Armazenar Histórico (Persistência em memória na sessão do Streamlit)
if 'sistema' not in st.session_state:
    st.session_state.sistema = SistemasContas()

st.title("⚡ Sistema de Acompanhamento de Gasto de Luz")
st.markdown("Interface para registro e análise de consumo de energia, baseada na planilha do Gabriel.")
st.divider()

col_form, col_dash = st.columns([1, 2], gap="large")

with col_form:
    st.header("📝 Registrar Conta")
    
    # RF01: Registrar Conta de Luz
    with st.form("form_registro_conta", clear_on_submit=True):
        datasLeitura = st.date_input("Data da Leitura", format="DD/MM/YYYY")
        numeroLeitura = st.number_input("Nº da Leitura", min_value=0, step=1)
        
        # RNF04: O sistema não deve permitir a entrada de valores negativos
        kwGasto = st.number_input("KW Gasto", min_value=0.0, step=1.0, format="%.2f")
        valoPagar = st.number_input("Valor a Pagar (R$)", min_value=0.0, step=0.01, format="%.2f")
        
        dataPagamento = st.date_input("Data do Pagamento", format="DD/MM/YYYY")
        mediaConsumo = st.number_input("Média de Consumo", min_value=0.0, step=0.01, format="%.2f")
        
        submit = st.form_submit_button("Adicionar Registro", use_container_width=True)
        
        if submit:
            nova_conta = ContaDeLuz(
                datasLeitura=datasLeitura,
                numeroLeitura=numeroLeitura,
                kwGasto=kwGasto,
                valoPagar=valoPagar,
                dataPagamento=dataPagamento,
                mediaConsumo=mediaConsumo
            )
            st.session_state.sistema.adicionarConta(nova_conta)
            st.success("Conta registrada com sucesso!")

with col_dash:
    st.header("📊 Painel de Análise")
    sistema = st.session_state.sistema
    
    if not sistema.contas:
        st.info("Nenhuma conta registrada ainda. Preencha o formulário ao lado para iniciar.")
    else:
        # RF02 e RF03: Identificar Menor e Maior Consumo
        conta_maior = sistema.obterMesMaiorConsumo()
        conta_menor = sistema.obterMesMenorConsumo()
        # RF05: Realizar média dos consumos
        media_geral = sistema.realizarMediaConsumos()
        
        # RNF02: Os valores de "Maior" e "Menor" consumo devem ser destacados visualmente
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.error(f"📈 **Maior Consumo**\n\n**{conta_maior.obterMesReferencia()}** - {conta_maior.obterConsumo():.0f} KW")
            
        with c2:
            st.success(f"📉 **Menor Consumo**\n\n**{conta_menor.obterMesReferencia()}** - {conta_menor.obterConsumo():.0f} KW")
            
        with c3:
            # RNF03: Garantir cálculos de média precisos
            st.info(f"⚖️ **Média Geral**\n\n**{media_geral:.2f}** KW/mês")
            
        st.divider()
        
        # Exibição do Histórico em formato de tabela
        st.subheader("Histórico de Acompanhamento")
        
        dados_tabela = []
        for conta in sistema.contas:
            dados_tabela.append({
                "Mês Ref.": conta.obterMesReferencia(),
                "Data Leitura": conta.datasLeitura.strftime("%d/%m/%Y"),
                "Nº Leitura": conta.numeroLeitura,
                "KW Gasto": conta.kwGasto,
                "Valor (R$)": f"R$ {conta.valoPagar:.2f}",
                "Data Pagamento": conta.dataPagamento.strftime("%d/%m/%Y"),
                "Média Consumo": conta.mediaConsumo
            })
            
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)