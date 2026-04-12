import streamlit as st
import json
import os
from datetime import date, time, datetime, timedelta
from typing import List, Optional

# ──────────────────────────────────────────────
# PERSISTÊNCIA (JSON em arquivo local)
# ──────────────────────────────────────────────
DATA_FILE = "medicamentos_data.json"

def carregar_dados() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dados_iniciais()

def salvar_dados(dados: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, default=str, indent=2)

def dados_iniciais() -> dict:
    return {
        "pacientes": [
            {"id": 1, "nome": "Maria Silva", "dataNascimento": "1985-03-20"},
            {"id": 2, "nome": "João Souza",  "dataNascimento": "1972-11-05"},
        ],
        "medicos": [
            {"id": 1, "nome": "Dr. Carlos Mendes", "crm": "CRM-SP 12345"},
            {"id": 2, "nome": "Dra. Ana Lima",     "crm": "CRM-SP 67890"},
        ],
        "atendimentos": [
            {
                "id": 1,
                "paciente_id": 1,
                "medico_id": 1,
                "dataInicio": "2025-07-01",
                "quantidadeDias": 10,
                "remedios": [
                    {
                        "id": 1,
                        "nome": "Amoxicilina",
                        "dosagem": "500mg",
                        "vezesAoDia": 3,
                        "horariosEscolhidos": ["08:00", "14:00", "20:00"],
                        "tomados": {}
                    }
                ],
                "planilha": None
            }
        ],
        "_seq": {"pacientes": 3, "medicos": 3, "atendimentos": 2, "remedios": 2}
    }

# ──────────────────────────────────────────────
# LÓGICA DE DOMÍNIO
# ──────────────────────────────────────────────
def proximo_id(dados: dict, entidade: str) -> int:
    seq = dados["_seq"].get(entidade, 1)
    dados["_seq"][entidade] = seq + 1
    return seq

def sugerir_horarios(vezes_ao_dia: int) -> List[str]:
    if vezes_ao_dia <= 0:
        return []
    inicio = 7
    fim = 22
    intervalo = (fim - inicio) / vezes_ao_dia
    horarios = []
    for i in range(vezes_ao_dia):
        hora_float = inicio + i * intervalo
        hora = int(hora_float)
        minuto = int((hora_float - hora) * 60)
        horarios.append(f"{hora:02d}:{minuto:02d}")
    return horarios

def calcular_data_fim(data_inicio_str: str, quantidade_dias: int) -> str:
    data_inicio = date.fromisoformat(data_inicio_str)
    data_fim = data_inicio + timedelta(days=quantidade_dias - 1)
    return data_fim.isoformat()

def gerar_planilha(atendimento: dict) -> dict:
    data_inicio = date.fromisoformat(atendimento["dataInicio"])
    quantidade_dias = atendimento["quantidadeDias"]
    planilha = {"data": atendimento["dataInicio"], "status": "ativa", "horariosPorDia": {}}
    for i in range(quantidade_dias):
        dia = (data_inicio + timedelta(days=i)).isoformat()
        entradas = []
        for rem in atendimento["remedios"]:
            for h in rem["horariosEscolhidos"]:
                entradas.append({
                    "remedio_id": rem["id"],
                    "remedio_nome": rem["nome"],
                    "dosagem": rem["dosagem"],
                    "horario": h,
                    "tomado": False
                })
        entradas.sort(key=lambda x: x["horario"])
        planilha["horariosPorDia"][dia] = entradas
    return planilha

def reorganizar_horarios_dia(planilha: dict, dia_str: str, atraso_minutos: int) -> dict:
    if dia_str not in planilha.get("horariosPorDia", {}):
        return planilha
    entradas = planilha["horariosPorDia"][dia_str]
    agora = datetime.now()
    for entrada in entradas:
        if not entrada["tomado"]:
            h, m = map(int, entrada["horario"].split(":"))
            horario_original = agora.replace(hour=h, minute=m, second=0, microsecond=0)
            novo = horario_original + timedelta(minutes=atraso_minutos)
            if novo.hour < 23:
                entrada["horario"] = f"{novo.hour:02d}:{novo.minute:02d}"
    planilha["horariosPorDia"][dia_str] = sorted(entradas, key=lambda x: x["horario"])
    return planilha

def nome_paciente(dados: dict, pid: int) -> str:
    for p in dados["pacientes"]:
        if p["id"] == pid:
            return p["nome"]
    return "—"

def nome_medico(dados: dict, mid: int) -> str:
    for m in dados["medicos"]:
        if m["id"] == mid:
            return m["nome"]
    return "—"

# ──────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="MedAgenda",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Fira+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f172a 0%, #1e3a5f 100%);
    color: #e2e8f0;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { font-weight: 600; font-size: 1rem; }

/* Cards */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
    border-left: 5px solid #3b82f6;
}
.card-green  { border-left-color: #22c55e; }
.card-purple { border-left-color: #8b5cf6; }
.card-orange { border-left-color: #f97316; }
.card-red    { border-left-color: #ef4444; }

.pill {
    display:inline-block;
    padding: 2px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 4px;
}
.pill-blue   { background:#dbeafe; color:#1d4ed8; }
.pill-green  { background:#dcfce7; color:#16a34a; }
.pill-orange { background:#fff7ed; color:#c2410c; }
.pill-red    { background:#fee2e2; color:#b91c1c; }

h1 { font-size: 2rem !important; font-weight: 800 !important; color: #0f172a !important; }
h2 { font-size: 1.4rem !important; font-weight: 700 !important; color: #1e3a5f !important; }
h3 { font-size: 1.1rem !important; font-weight: 700 !important; color: #334155 !important; }

.metric-box {
    background: linear-gradient(135deg, #1e3a5f, #3b82f6);
    color: white;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
}
.metric-box .num { font-size: 2.2rem; font-weight: 800; }
.metric-box .lbl { font-size: 0.85rem; opacity: 0.85; }

.horario-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    margin: 6px 0;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
}
.horario-item.tomado { background: #f0fdf4; border-color: #86efac; }
.horario-time { font-family: 'Fira Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #3b82f6; min-width: 60px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

dados = st.session_state.dados

# ──────────────────────────────────────────────
# SIDEBAR / NAVEGAÇÃO
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💊 MedAgenda")
    st.markdown("---")
    pagina = st.radio("Navegação", [
        "🏠 Início",
        "👤 Pacientes",
        "🩺 Médicos",
        "📋 Atendimentos",
        "💊 Remédios",
        "📅 Planilha Diária",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Sistema de controle pessoal de medicamentos")

# ──────────────────────────────────────────────
# PÁGINA: INÍCIO
# ──────────────────────────────────────────────
if pagina == "🏠 Início":
    st.title("🏠 MedAgenda")
    st.markdown("##### Controle inteligente de medicamentos e horários")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="num">{len(dados["pacientes"])}</div><div class="lbl">Pacientes</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="num">{len(dados["medicos"])}</div><div class="lbl">Médicos</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="num">{len(dados["atendimentos"])}</div><div class="lbl">Atendimentos</div></div>', unsafe_allow_html=True)
    with c4:
        total_rem = sum(len(a["remedios"]) for a in dados["atendimentos"])
        st.markdown(f'<div class="metric-box"><div class="num">{total_rem}</div><div class="lbl">Remédios</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📅 Atendimentos Ativos")

    hoje = date.today().isoformat()
    ativos = [a for a in dados["atendimentos"]
              if a["dataInicio"] <= hoje <= calcular_data_fim(a["dataInicio"], a["quantidadeDias"])]

    if not ativos:
        st.info("Nenhum atendimento ativo hoje.")
    for at in ativos:
        data_fim = calcular_data_fim(at["dataInicio"], at["quantidadeDias"])
        remedios_nomes = ", ".join(r["nome"] for r in at["remedios"]) or "—"
        st.markdown(f"""
        <div class="card">
            <h3>👤 {nome_paciente(dados, at["paciente_id"])} &nbsp;
                <span class="pill pill-blue">🩺 {nome_medico(dados, at["medico_id"])}</span>
            </h3>
            <p>💊 <b>Remédios:</b> {remedios_nomes}<br>
               📆 <b>Período:</b> {at["dataInicio"]} → {data_fim} ({at["quantidadeDias"]} dias)</p>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PÁGINA: PACIENTES
# ──────────────────────────────────────────────
elif pagina == "👤 Pacientes":
    st.title("👤 Pacientes")

    with st.expander("➕ Cadastrar Novo Paciente", expanded=False):
        with st.form("form_paciente"):
            nome = st.text_input("Nome completo *")
            dn   = st.date_input("Data de nascimento *", value=date(1990, 1, 1))
            if st.form_submit_button("💾 Salvar"):
                if not nome.strip():
                    st.error("Nome é obrigatório.")
                else:
                    novo = {"id": proximo_id(dados, "pacientes"), "nome": nome.strip(), "dataNascimento": dn.isoformat()}
                    dados["pacientes"].append(novo)
                    salvar_dados(dados)
                    st.success(f"Paciente **{nome}** cadastrado!")
                    st.rerun()

    st.markdown("---")
    busca = st.text_input("🔍 Buscar paciente", placeholder="Digite o nome...")
    lista = [p for p in dados["pacientes"] if busca.lower() in p["nome"].lower()]

    if not lista:
        st.info("Nenhum paciente encontrado.")
    for p in lista:
        atends = [a for a in dados["atendimentos"] if a["paciente_id"] == p["id"]]
        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div class="card card-purple">
                    <h3>👤 {p["nome"]}</h3>
                    <p>🎂 Nascimento: <b>{p["dataNascimento"]}</b> &nbsp;|&nbsp;
                       📋 Atendimentos: <b>{len(atends)}</b></p>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_pac_{p['id']}", help="Remover paciente"):
                    dados["pacientes"] = [x for x in dados["pacientes"] if x["id"] != p["id"]]
                    salvar_dados(dados)
                    st.rerun()

# ──────────────────────────────────────────────
# PÁGINA: MÉDICOS
# ──────────────────────────────────────────────
elif pagina == "🩺 Médicos":
    st.title("🩺 Médicos")

    with st.expander("➕ Cadastrar Novo Médico", expanded=False):
        with st.form("form_medico"):
            nome = st.text_input("Nome completo *")
            crm  = st.text_input("CRM *")
            if st.form_submit_button("💾 Salvar"):
                if not nome.strip() or not crm.strip():
                    st.error("Nome e CRM são obrigatórios.")
                else:
                    novo = {"id": proximo_id(dados, "medicos"), "nome": nome.strip(), "crm": crm.strip()}
                    dados["medicos"].append(novo)
                    salvar_dados(dados)
                    st.success(f"Médico **{nome}** cadastrado!")
                    st.rerun()

    st.markdown("---")
    busca = st.text_input("🔍 Buscar médico", placeholder="Nome ou CRM...")
    lista = [m for m in dados["medicos"] if busca.lower() in m["nome"].lower() or busca.lower() in m["crm"].lower()]

    if not lista:
        st.info("Nenhum médico encontrado.")
    for m in lista:
        atends = [a for a in dados["atendimentos"] if a["medico_id"] == m["id"]]
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="card card-green">
                <h3>🩺 {m["nome"]}</h3>
                <p>📋 CRM: <b>{m["crm"]}</b> &nbsp;|&nbsp; Atendimentos: <b>{len(atends)}</b></p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_med_{m['id']}", help="Remover médico"):
                dados["medicos"] = [x for x in dados["medicos"] if x["id"] != m["id"]]
                salvar_dados(dados)
                st.rerun()

# ──────────────────────────────────────────────
# PÁGINA: ATENDIMENTOS
# ──────────────────────────────────────────────
elif pagina == "📋 Atendimentos":
    st.title("📋 Atendimentos")

    with st.expander("➕ Novo Atendimento", expanded=False):
        with st.form("form_atendimento"):
            pacs = {p["nome"]: p["id"] for p in dados["pacientes"]}
            meds_dict = {m["nome"]: m["id"] for m in dados["medicos"]}
            if not pacs:
                st.warning("Cadastre ao menos um paciente antes.")
            elif not meds_dict:
                st.warning("Cadastre ao menos um médico antes.")
            else:
                pac_sel  = st.selectbox("Paciente *", list(pacs.keys()))
                med_sel  = st.selectbox("Médico *",   list(meds_dict.keys()))
                d_inicio = st.date_input("Data de início *", value=date.today())
                qtd_dias = st.number_input("Quantidade de dias *", min_value=1, max_value=365, value=7)
                if st.form_submit_button("💾 Criar Atendimento"):
                    novo = {
                        "id": proximo_id(dados, "atendimentos"),
                        "paciente_id": pacs[pac_sel],
                        "medico_id":   meds_dict[med_sel],
                        "dataInicio":  d_inicio.isoformat(),
                        "quantidadeDias": int(qtd_dias),
                        "remedios": [],
                        "planilha": None
                    }
                    dados["atendimentos"].append(novo)
                    salvar_dados(dados)
                    st.success("Atendimento criado!")
                    st.rerun()

    st.markdown("---")
    if not dados["atendimentos"]:
        st.info("Nenhum atendimento cadastrado.")

    for at in dados["atendimentos"]:
        data_fim = calcular_data_fim(at["dataInicio"], at["quantidadeDias"])
        hoje = date.today().isoformat()
        ativo = at["dataInicio"] <= hoje <= data_fim
        status_html = '<span class="pill pill-green">✅ Ativo</span>' if ativo else '<span class="pill pill-red">⏹ Encerrado</span>'
        remedios_txt = ", ".join(r["nome"] for r in at["remedios"]) or "Nenhum remédio"

        st.markdown(f"""
        <div class="card {'card-green' if ativo else ''}">
            <h3>👤 {nome_paciente(dados, at["paciente_id"])} &nbsp; {status_html}</h3>
            <p>🩺 <b>{nome_medico(dados, at["medico_id"])}</b><br>
               📆 {at["dataInicio"]} → {data_fim} ({at["quantidadeDias"]} dias)<br>
               💊 {remedios_txt}</p>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if at["planilha"] is None:
                if at["remedios"] and st.button("📅 Gerar Planilha", key=f"gpl_{at['id']}"):
                    at["planilha"] = gerar_planilha(at)
                    salvar_dados(dados)
                    st.success("Planilha gerada!")
                    st.rerun()
            else:
                st.markdown('<span class="pill pill-blue">📅 Planilha gerada</span>', unsafe_allow_html=True)
        with col2:
            if st.button("🗑️ Remover", key=f"del_at_{at['id']}"):
                dados["atendimentos"] = [x for x in dados["atendimentos"] if x["id"] != at["id"]]
                salvar_dados(dados)
                st.rerun()
        st.markdown("---")

# ──────────────────────────────────────────────
# PÁGINA: REMÉDIOS
# ──────────────────────────────────────────────
elif pagina == "💊 Remédios":
    st.title("💊 Remédios")

    if not dados["atendimentos"]:
        st.warning("Crie um atendimento primeiro.")
    else:
        # Selecionar atendimento
        at_labels = {
            f"{nome_paciente(dados, a['paciente_id'])} — {a['dataInicio']} ({a['quantidadeDias']}d)": a["id"]
            for a in dados["atendimentos"]
        }
        sel_label = st.selectbox("Selecionar atendimento", list(at_labels.keys()))
        at_id = at_labels[sel_label]
        atendimento = next(a for a in dados["atendimentos"] if a["id"] == at_id)

        st.markdown("---")
        st.subheader("➕ Cadastrar Remédio")

        with st.form("form_remedio"):
            nome_rem  = st.text_input("Nome do remédio *")
            dosagem   = st.text_input("Dosagem *", placeholder="ex: 500mg")
            vezes     = st.number_input("Vezes ao dia *", min_value=1, max_value=24, value=2)
            sugeridos = sugerir_horarios(int(vezes)) if vezes > 0 else []

            st.markdown(f"**Horários sugeridos:** {', '.join(sugeridos) if sugeridos else '—'}")
            horarios_texto = st.text_input(
                "Confirme/ajuste os horários (separados por vírgula)",
                value=", ".join(sugeridos)
            )

            if st.form_submit_button("💾 Cadastrar Remédio"):
                if not nome_rem.strip() or not dosagem.strip():
                    st.error("Nome e dosagem são obrigatórios.")
                else:
                    horarios_final = [h.strip() for h in horarios_texto.split(",") if h.strip()]
                    novo_rem = {
                        "id": proximo_id(dados, "remedios"),
                        "nome": nome_rem.strip(),
                        "dosagem": dosagem.strip(),
                        "vezesAoDia": int(vezes),
                        "horariosEscolhidos": horarios_final,
                        "tomados": {}
                    }
                    atendimento["remedios"].append(novo_rem)
                    # Regenerar planilha se existia
                    if atendimento["planilha"] is not None:
                        atendimento["planilha"] = gerar_planilha(atendimento)
                    salvar_dados(dados)
                    st.success(f"Remédio **{nome_rem}** cadastrado!")
                    st.rerun()

        # Listar remédios
        st.markdown("---")
        st.subheader("📋 Remédios Cadastrados neste Atendimento")
        if not atendimento["remedios"]:
            st.info("Nenhum remédio cadastrado neste atendimento.")
        for rem in atendimento["remedios"]:
            data_fim = calcular_data_fim(atendimento["dataInicio"], atendimento["quantidadeDias"])
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div class="card card-orange">
                    <h3>💊 {rem["nome"]} <span class="pill pill-orange">{rem["dosagem"]}</span></h3>
                    <p>🕐 {rem["vezesAoDia"]}x ao dia &nbsp;|&nbsp;
                       Horários: <b>{', '.join(rem["horariosEscolhidos"])}</b><br>
                       📅 Até: <b>{data_fim}</b></p>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_rem_{rem['id']}"):
                    atendimento["remedios"] = [r for r in atendimento["remedios"] if r["id"] != rem["id"]]
                    if atendimento["planilha"] is not None:
                        atendimento["planilha"] = gerar_planilha(atendimento) if atendimento["remedios"] else None
                    salvar_dados(dados)
                    st.rerun()

# ──────────────────────────────────────────────
# PÁGINA: PLANILHA DIÁRIA
# ──────────────────────────────────────────────
elif pagina == "📅 Planilha Diária":
    st.title("📅 Planilha Diária de Horários")

    atendimentos_com_planilha = [a for a in dados["atendimentos"] if a["planilha"] is not None]

    if not atendimentos_com_planilha:
        st.info("Nenhum atendimento com planilha gerada. Vá em **📋 Atendimentos** e gere a planilha.")
    else:
        at_labels = {
            f"{nome_paciente(dados, a['paciente_id'])} — {a['dataInicio']}": a["id"]
            for a in atendimentos_com_planilha
        }
        sel_label = st.selectbox("Selecionar atendimento", list(at_labels.keys()))
        at_id = at_labels[sel_label]
        atendimento = next(a for a in dados["atendimentos"] if a["id"] == at_id)
        planilha = atendimento["planilha"]

        dias_disponiveis = sorted(planilha["horariosPorDia"].keys())
        dia_sel = st.selectbox(
            "📆 Selecionar dia",
            dias_disponiveis,
            index=min(
                next((i for i, d in enumerate(dias_disponiveis) if d >= date.today().isoformat()), 0),
                len(dias_disponiveis) - 1
            )
        )

        st.markdown("---")
        col_info, col_reorg = st.columns([3, 2])
        with col_info:
            st.subheader(f"🗓️ {dia_sel}")
        with col_reorg:
            with st.expander("⏰ Reorganizar por atraso"):
                with st.form("form_reorg"):
                    atraso = st.number_input("Minutos de atraso", min_value=1, max_value=240, value=30)
                    if st.form_submit_button("🔄 Reorganizar"):
                        atendimento["planilha"] = reorganizar_horarios_dia(planilha, dia_sel, int(atraso))
                        salvar_dados(dados)
                        st.success(f"Horários reorganizados com +{atraso} min.")
                        st.rerun()

        entradas = planilha["horariosPorDia"].get(dia_sel, [])
        if not entradas:
            st.info("Nenhum horário para este dia.")
        else:
            total = len(entradas)
            tomados = sum(1 for e in entradas if e["tomado"])
            st.markdown(f"**Progresso do dia:** {tomados}/{total} doses tomadas")
            prog = tomados / total if total > 0 else 0
            st.progress(prog)
            st.markdown("")

            for i, entrada in enumerate(entradas):
                cls = "horario-item tomado" if entrada["tomado"] else "horario-item"
                status_icon = "✅" if entrada["tomado"] else "⏳"
                col_card, col_btn = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="{cls}">
                        <span class="horario-time">🕐 {entrada["horario"]}</span>
                        <span>{status_icon} <b>{entrada["remedio_nome"]}</b> — {entrada["dosagem"]}</span>
                    </div>""", unsafe_allow_html=True)
                with col_btn:
                    label_btn = "↩️" if entrada["tomado"] else "✅"
                    if st.button(label_btn, key=f"tom_{dia_sel}_{i}"):
                        planilha["horariosPorDia"][dia_sel][i]["tomado"] = not entrada["tomado"]
                        salvar_dados(dados)
                        st.rerun()

        st.markdown("---")
        # Visão geral da semana
        st.subheader("📊 Visão Geral — Todos os Dias")
        resumo = []
        for dia, ents in sorted(planilha["horariosPorDia"].items()):
            tom = sum(1 for e in ents if e["tomado"])
            tot = len(ents)
            resumo.append({"Dia": dia, "Doses tomadas": tom, "Total": tot, "% Adesão": f"{int(tom/tot*100) if tot else 0}%"})

        st.dataframe(resumo, use_container_width=True, hide_index=True)