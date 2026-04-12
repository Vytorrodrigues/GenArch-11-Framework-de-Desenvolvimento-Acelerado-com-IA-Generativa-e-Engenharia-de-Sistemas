"""
Sistema de Agendamento de Salas de Reunião
Arquivo único executável: streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import date, time, datetime, timedelta
from typing import Optional
import calendar

# ─────────────────────────────────────────────
# CONFIGURAÇÃO GLOBAL
# ─────────────────────────────────────────────
DATA_FILE = "agendamento_data.json"
USUARIOS = {
    "admin": {"senha": "admin123", "perfil": "admin"},
    "patricia": {"senha": "reuniao", "perfil": "admin"},
    "visitante": {"senha": "ver123", "perfil": "viewer"},
}

# ─────────────────────────────────────────────
# PERSISTÊNCIA JSON
# ─────────────────────────────────────────────

def carregar_dados() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dados_iniciais()

def salvar_dados(dados: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def dados_iniciais() -> dict:
    return {
        "salas": [
            {"codigo": "101", "capacidade": 8},
            {"codigo": "202", "capacidade": 15},
            {"codigo": "303", "capacidade": 4},
            {"codigo": "Auditório", "capacidade": 50},
        ],
        "funcionarios": [
            {"nome": "Patrícia Souza", "cargo": "Gerente de Projetos", "ramal": "1001"},
            {"nome": "Carlos Lima", "cargo": "Analista de TI", "ramal": "1042"},
            {"nome": "Fernanda Rocha", "cargo": "RH", "ramal": "1055"},
            {"nome": "Rafael Mendes", "cargo": "Diretor Comercial", "ramal": "2010"},
        ],
        "reunioes": [
            {
                "id": "r1",
                "data": str(date.today()),
                "hora_inicio": "09:00",
                "hora_fim": "10:00",
                "sala": "101",
                "funcionario": "Patrícia Souza",
                "assunto": "Planejamento Q2",
            },
            {
                "id": "r2",
                "data": str(date.today()),
                "hora_inicio": "14:00",
                "hora_fim": "15:30",
                "sala": "202",
                "funcionario": "Carlos Lima",
                "assunto": "Revisão de Sistemas",
            },
            {
                "id": "r3",
                "data": str(date.today() + timedelta(days=1)),
                "hora_inicio": "10:00",
                "hora_fim": "11:00",
                "sala": "303",
                "funcionario": "Fernanda Rocha",
                "assunto": "Entrevistas",
            },
        ],
    }

# ─────────────────────────────────────────────
# MODELO DE DOMÍNIO
# ─────────────────────────────────────────────

class Sala:
    def __init__(self, codigo: str, capacidade: int):
        self.codigo = codigo
        self.capacidade = capacidade

    def esta_livre(self, data: str, inicio: str, fim: str, reunioes: list, excluir_id: str = None) -> bool:
        for r in reunioes:
            if r["sala"] != self.codigo or r["data"] != data:
                continue
            if excluir_id and r["id"] == excluir_id:
                continue
            if horarios_sobrepoem(inicio, fim, r["hora_inicio"], r["hora_fim"]):
                return False
        return True

    def get_agendamentos(self, reunioes: list) -> list:
        return [r for r in reunioes if r["sala"] == self.codigo]

    def to_dict(self):
        return {"codigo": self.codigo, "capacidade": self.capacidade}


class Funcionario:
    def __init__(self, nome: str, cargo: str, ramal: str):
        self.nome = nome
        self.cargo = cargo
        self.ramal = ramal

    def get_reunioes(self, reunioes: list) -> list:
        return [r for r in reunioes if r["funcionario"] == self.nome]

    def to_dict(self):
        return {"nome": self.nome, "cargo": self.cargo, "ramal": self.ramal}


class Reuniao:
    def __init__(self, id: str, data: str, hora_inicio: str, hora_fim: str,
                 sala: str, funcionario: str, assunto: str):
        self.id = id
        self.data = data
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.sala = sala
        self.funcionario = funcionario
        self.assunto = assunto

    def realocar(self, nova_sala: str, nova_data: str, novo_inicio: str, novo_fim: str):
        self.sala = nova_sala
        self.data = nova_data
        self.hora_inicio = novo_inicio
        self.hora_fim = novo_fim

    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data,
            "hora_inicio": self.hora_inicio,
            "hora_fim": self.hora_fim,
            "sala": self.sala,
            "funcionario": self.funcionario,
            "assunto": self.assunto,
        }


class SistemaAgendamento:
    def __init__(self, dados: dict):
        self.salas = [Sala(s["codigo"], s["capacidade"]) for s in dados["salas"]]
        self.funcionarios = [Funcionario(f["nome"], f["cargo"], f["ramal"]) for f in dados["funcionarios"]]
        self.reunioes = dados["reunioes"]

    def to_dict(self):
        return {
            "salas": [s.to_dict() for s in self.salas],
            "funcionarios": [f.to_dict() for f in self.funcionarios],
            "reunioes": self.reunioes,
        }

    def cadastrar_sala(self, codigo: str, capacidade: int) -> tuple[bool, str]:
        if any(s.codigo == codigo for s in self.salas):
            return False, f"Sala '{codigo}' já existe."
        self.salas.append(Sala(codigo, capacidade))
        return True, f"Sala '{codigo}' cadastrada com sucesso."

    def remover_sala(self, codigo: str) -> tuple[bool, str]:
        if any(r["sala"] == codigo for r in self.reunioes):
            return False, "Sala possui reuniões agendadas. Remova-as primeiro."
        self.salas = [s for s in self.salas if s.codigo != codigo]
        return True, f"Sala '{codigo}' removida."

    def manter_funcionario(self, nome: str, cargo: str, ramal: str, nome_original: str = None) -> tuple[bool, str]:
        if nome_original:
            for f in self.funcionarios:
                if f.nome == nome_original:
                    f.nome = nome
                    f.cargo = cargo
                    f.ramal = ramal
                    # Atualizar referências em reuniões
                    for r in self.reunioes:
                        if r["funcionario"] == nome_original:
                            r["funcionario"] = nome
                    return True, "Funcionário atualizado."
            return False, "Funcionário não encontrado."
        if any(f.nome == nome for f in self.funcionarios):
            return False, f"Funcionário '{nome}' já cadastrado."
        self.funcionarios.append(Funcionario(nome, cargo, ramal))
        return True, f"Funcionário '{nome}' cadastrado."

    def remover_funcionario(self, nome: str) -> tuple[bool, str]:
        if any(r["funcionario"] == nome for r in self.reunioes):
            return False, "Funcionário possui reuniões agendadas."
        self.funcionarios = [f for f in self.funcionarios if f.nome != nome]
        return True, f"Funcionário '{nome}' removido."

    def agendar_reuniao(self, sala_cod: str, data: str, inicio: str, fim: str,
                        funcionario: str, assunto: str) -> tuple[bool, str]:
        sala = self._get_sala(sala_cod)
        if not sala:
            return False, "Sala não encontrada."
        if inicio >= fim:
            return False, "Horário de início deve ser anterior ao fim."
        if not sala.esta_livre(data, inicio, fim, self.reunioes):
            return False, f"Sala '{sala_cod}' já possui reunião nesse horário."
        novo_id = f"r{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        reuniao = Reuniao(novo_id, data, inicio, fim, sala_cod, funcionario, assunto)
        self.reunioes.append(reuniao.to_dict())
        return True, "Reunião agendada com sucesso."

    def realocar_reuniao(self, reuniao_id: str, nova_sala: str, nova_data: str,
                         novo_inicio: str, novo_fim: str) -> tuple[bool, str]:
        r = next((x for x in self.reunioes if x["id"] == reuniao_id), None)
        if not r:
            return False, "Reunião não encontrada."
        sala = self._get_sala(nova_sala)
        if not sala:
            return False, "Sala não encontrada."
        if novo_inicio >= novo_fim:
            return False, "Horário inválido."
        if not sala.esta_livre(nova_data, novo_inicio, novo_fim, self.reunioes, excluir_id=reuniao_id):
            return False, f"Sala '{nova_sala}' já ocupada nesse horário."
        r["sala"] = nova_sala
        r["data"] = nova_data
        r["hora_inicio"] = novo_inicio
        r["hora_fim"] = novo_fim
        return True, "Reunião realocada com sucesso."

    def excluir_reuniao(self, reuniao_id: str) -> tuple[bool, str]:
        antes = len(self.reunioes)
        self.reunioes = [r for r in self.reunioes if r["id"] != reuniao_id]
        if len(self.reunioes) < antes:
            return True, "Reunião excluída."
        return False, "Reunião não encontrada."

    def consultar_salas_livres(self, data: str, inicio: str, fim: str) -> list:
        livres = []
        for sala in self.salas:
            if sala.esta_livre(data, inicio, fim, self.reunioes):
                livres.append(sala)
        return livres

    def exibir_agenda_dia(self, data: str) -> dict:
        grade = {}
        for sala in self.salas:
            grade[sala.codigo] = []
            for r in self.reunioes:
                if r["data"] == data and r["sala"] == sala.codigo:
                    grade[sala.codigo].append(r)
        return grade

    def exibir_agenda_mes(self, ano: int, mes: int) -> dict:
        grade = {}
        num_dias = calendar.monthrange(ano, mes)[1]
        for dia in range(1, num_dias + 1):
            data_str = f"{ano}-{mes:02d}-{dia:02d}"
            reunioes_dia = [r for r in self.reunioes if r["data"] == data_str]
            if reunioes_dia:
                grade[data_str] = reunioes_dia
        return grade

    def pesquisar_reunioes(self, data: str = None, sala: str = None, funcionario: str = None) -> list:
        resultado = self.reunioes
        if data:
            resultado = [r for r in resultado if r["data"] == data]
        if sala:
            resultado = [r for r in resultado if r["sala"] == sala]
        if funcionario:
            resultado = [r for r in resultado if r["funcionario"] == funcionario]
        return sorted(resultado, key=lambda r: (r["data"], r["hora_inicio"]))

    def _get_sala(self, codigo: str) -> Optional[Sala]:
        return next((s for s in self.salas if s.codigo == codigo), None)


# ─────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────

def horarios_sobrepoem(ini1: str, fim1: str, ini2: str, fim2: str) -> bool:
    return ini1 < fim2 and fim1 > ini2

def gerar_slots_horario():
    slots = []
    for h in range(7, 22):
        for m in (0, 30):
            slots.append(f"{h:02d}:{m:02d}")
    return slots

def novo_id() -> str:
    return f"r{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

def cor_sala(codigo: str) -> str:
    cores = ["#4F86C6", "#E07B54", "#5BAD72", "#9B59B6", "#E67E22", "#1ABC9C"]
    idx = hash(codigo) % len(cores)
    return cores[idx]

# ─────────────────────────────────────────────
# AUTENTICAÇÃO
# ─────────────────────────────────────────────

def tela_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem;">
            <div style="font-size:3rem;">🏢</div>
            <h1 style="font-family:'DM Serif Display',serif; font-size:2rem; margin:0.5rem 0 0.2rem;">
                SalaSync
            </h1>
            <p style="color:#ccc; font-size:0.95rem; margin:0;">Sistema de Agendamento de Salas</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            entrar = st.form_submit_button("Entrar", use_container_width=True, type="primary")

        if entrar:
            if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.session_state["perfil"] = USUARIOS[usuario]["perfil"]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

        st.markdown("""
        <div style="margin-top:1.5rem; padding:1rem; background:#f8f8f8; border-radius:8px; font-size:0.82rem; color:#666;">
            <b>Credenciais de teste:</b><br>
            admin / admin123 &nbsp;|&nbsp; patricia / reuniao &nbsp;|&nbsp; visitante / ver123
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────

def injetar_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem !important;
        padding: 0.4rem 0.2rem !important;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 0.8rem;
        border-left: 4px solid #4F86C6;
    }
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 0.3rem;
    }
    .card-sub {
        font-size: 0.85rem;
        color: #64748b;
    }
    .badge {
        display: inline-block;
        padding: 0.2em 0.7em;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        background: #e0f2fe;
        color: #0369a1;
        margin-right: 0.3rem;
    }

    /* Grade de horários */
    .grade-header {
        background: #0f172a;
        color: white;
        padding: 0.5rem;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        text-align: center;
        font-size: 0.85rem;
    }
    .slot-livre {
        background: #f1f5f9;
        border: 1px dashed #cbd5e1;
        border-radius: 4px;
        padding: 0.3rem;
        text-align: center;
        font-size: 0.75rem;
        color: #94a3b8;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .slot-ocupado {
        border-radius: 4px;
        padding: 0.3rem 0.5rem;
        font-size: 0.75rem;
        color: white;
        font-weight: 600;
        height: 40px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
    }

    /* KPI cards */
    .kpi {
        background: linear-gradient(135deg, #4F86C6, #2563eb);
        color: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .kpi-num {
        font-family: 'DM Serif Display', serif;
        font-size: 2.2rem;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.82rem;
        opacity: 0.85;
        margin-top: 0.3rem;
    }

    div[data-testid="stForm"] {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }

    .stButton > button[kind="primary"] {
        background: #16a34a !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    h1, h2, h3 {
        font-family: 'DM Serif Display', serif !important;
        color: #ffffff !important;
    }
    p {
        color: #ccc !important;
    }
    .st-emotion-cache-1bd5s7o{
        background-color: #2563eb!important;
        border: 1px solid #1d4ed8 !important;
        
    }
    .stAlertContainer{
    background-color: #dc2626 !important;            
                }  
    
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PÁGINAS
# ─────────────────────────────────────────────

def pagina_dashboard(sistema: SistemaAgendamento):
    st.title("Dashboard")
    hoje = str(date.today())
    reunioes_hoje = [r for r in sistema.reunioes if r["data"] == hoje]
    reunioes_semana = [r for r in sistema.reunioes
                       if hoje <= r["data"] <= str(date.today() + timedelta(days=7))]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi">
            <div class="kpi-num">{len(sistema.salas)}</div>
            <div class="kpi-label">Salas Cadastradas</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi" style="background:linear-gradient(135deg,#5BAD72,#16a34a)">
            <div class="kpi-num">{len(sistema.funcionarios)}</div>
            <div class="kpi-label">Funcionários</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi" style="background:linear-gradient(135deg,#E07B54,#dc2626)">
            <div class="kpi-num">{len(reunioes_hoje)}</div>
            <div class="kpi-label">Reuniões Hoje</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi" style="background:linear-gradient(135deg,#9B59B6,#7c3aed)">
            <div class="kpi-num">{len(reunioes_semana)}</div>
            <div class="kpi-label">Próximos 7 dias</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Reuniões de Hoje")
        if reunioes_hoje:
            for r in sorted(reunioes_hoje, key=lambda x: x["hora_inicio"]):
                cor = cor_sala(r["sala"])
                st.markdown(f"""
                <div class="card" style="border-left-color:{cor}">
                    <div class="card-title">🕐 {r['hora_inicio']} – {r['hora_fim']} &nbsp;
                        <span class="badge" style="background:{cor}20;color:{cor}">Sala {r['sala']}</span>
                    </div>
                    <div class="card-sub">{r['assunto']}</div>
                    <div class="card-sub">👤 {r['funcionario']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Nenhuma reunião agendada para hoje.")

    with col_b:
        st.subheader("Próximas Reuniões (7 dias)")
        futuras = [r for r in reunioes_semana if r["data"] > hoje]
        if futuras:
            for r in sorted(futuras, key=lambda x: (x["data"], x["hora_inicio"]))[:8]:
                data_fmt = datetime.strptime(r["data"], "%Y-%m-%d").strftime("%d/%m")
                cor = cor_sala(r["sala"])
                st.markdown(f"""
                <div class="card" style="border-left-color:{cor}">
                    <div class="card-title">{data_fmt} · {r['hora_inicio']}–{r['hora_fim']} &nbsp;
                        <span class="badge" style="background:{cor}20;color:{cor}">Sala {r['sala']}</span>
                    </div>
                    <div class="card-sub">{r['assunto']} · {r['funcionario']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Nenhuma reunião futura nos próximos 7 dias.")


def pagina_agenda_dia(sistema: SistemaAgendamento):
    st.title("Agenda do Dia")
    data_sel = st.date_input("Selecione a data", value=date.today())
    data_str = str(data_sel)

    grade = sistema.exibir_agenda_dia(data_str)
    slots = gerar_slots_horario()

    # Montar mapeamento rápido sala→slot→reuniao
    mapa = {sala: {} for sala in grade}
    for sala_cod, reunioes in grade.items():
        for r in reunioes:
            for slot in slots:
                if r["hora_inicio"] <= slot < r["hora_fim"]:
                    mapa[sala_cod][slot] = r

    # Cabeçalho
    colunas = ["Horário"] + list(grade.keys())
    num_cols = len(colunas)
    cols = st.columns(num_cols)
    for i, c in enumerate(colunas):
        with cols[i]:
            lbl = c if i > 0 else ""
            st.markdown(f'<div class="grade-header">{lbl if lbl else "⏰ Hora"}</div>', unsafe_allow_html=True)

    # Linhas de hora
    slots_exibir = [s for s in slots if "07:00" <= s <= "20:30"]
    slot_anterior = {sala: None for sala in grade}

    for slot in slots_exibir:
        cols = st.columns(num_cols)
        with cols[0]:
            st.markdown(f'<div style="font-size:0.8rem;color:#64748b;padding:0.4rem 0;text-align:right;border-right:2px solid #e2e8f0;padding-right:0.5rem;">{slot}</div>', unsafe_allow_html=True)
        for i, sala_cod in enumerate(grade.keys(), start=1):
            with cols[i]:
                reuniao = mapa[sala_cod].get(slot)
                if reuniao:
                    if reuniao != slot_anterior[sala_cod]:
                        cor = cor_sala(sala_cod)
                        st.markdown(f"""<div class="slot-ocupado" style="background:{cor}">
                            <span>{reuniao['assunto'][:18]}</span>
                            <span style="font-weight:300;font-size:0.7rem">{reuniao['funcionario'].split()[0]}</span>
                        </div>""", unsafe_allow_html=True)
                        slot_anterior[sala_cod] = reuniao
                    else:
                        cor = cor_sala(sala_cod)
                        st.markdown(f'<div style="background:{cor};height:40px;border-top:1px solid rgba(255,255,255,0.3);border-radius:0;"></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="slot-livre">—</div>', unsafe_allow_html=True)
                    slot_anterior[sala_cod] = None


def pagina_agenda_mes(sistema: SistemaAgendamento):
    st.title("Agenda do Mês")

    col1, col2 = st.columns(2)
    with col1:
        ano = st.number_input("Ano", min_value=2020, max_value=2035, value=date.today().year)
    with col2:
        mes = st.selectbox("Mês", list(range(1, 13)),
                           index=date.today().month - 1,
                           format_func=lambda m: calendar.month_name[m])

    grade = sistema.exibir_agenda_mes(int(ano), int(mes))
    num_dias = calendar.monthrange(int(ano), int(mes))[1]

    st.markdown(f"#### {calendar.month_name[int(mes)]} {int(ano)}")

    # Calendário visual
    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    cols_header = st.columns(7)
    for i, d in enumerate(dias_semana):
        with cols_header[i]:
            st.markdown(f'<div style="text-align:center;font-weight:600;color:#64748b;font-size:0.85rem;padding:0.3rem">{d}</div>', unsafe_allow_html=True)

    primeiro_dia = date(int(ano), int(mes), 1).weekday()
    dias = [""] * primeiro_dia + list(range(1, num_dias + 1))
    while len(dias) % 7 != 0:
        dias.append("")

    semanas = [dias[i:i+7] for i in range(0, len(dias), 7)]
    hoje_str = str(date.today())

    for semana in semanas:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia == "":
                    st.markdown('<div style="height:70px"></div>', unsafe_allow_html=True)
                else:
                    data_str = f"{int(ano)}-{int(mes):02d}-{dia:02d}"
                    reunioes = grade.get(data_str, [])
                    n = len(reunioes)
                    is_hoje = data_str == hoje_str
                    borda = "3px solid #2563eb" if is_hoje else "1px solid #e2e8f0"
                    bg = "#eff6ff" if is_hoje else "white"
                    cor_num = "#2563eb" if is_hoje else "#0f172a"

                    items_html = ""
                    for r in reunioes[:2]:
                        cor = cor_sala(r["sala"])
                        items_html += f'<div style="background:{cor};color:white;font-size:0.65rem;padding:1px 4px;border-radius:3px;margin-top:2px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">{r["hora_inicio"]} {r["assunto"][:12]}</div>'
                    if n > 2:
                        items_html += f'<div style="font-size:0.65rem;color:#64748b;margin-top:2px">+{n-2} mais</div>'

                    st.markdown(f"""
                    <div style="border:{borda};background:{bg};border-radius:8px;padding:0.4rem 0.5rem;height:80px;overflow:hidden;cursor:pointer;">
                        <div style="font-weight:600;color:{cor_num};font-size:0.9rem">{dia}</div>
                        {items_html}
                    </div>""", unsafe_allow_html=True)

    # Detalhe do dia selecionado
    st.markdown("---")
    st.subheader("Detalhe do Dia")
    dia_sel = st.selectbox("Selecione o dia", list(range(1, num_dias + 1)))
    data_detalhe = f"{int(ano)}-{int(mes):02d}-{int(dia_sel):02d}"
    reunioes_dia = grade.get(data_detalhe, [])

    if reunioes_dia:
        for r in sorted(reunioes_dia, key=lambda x: x["hora_inicio"]):
            cor = cor_sala(r["sala"])
            st.markdown(f"""
            <div class="card" style="border-left-color:{cor}">
                <div class="card-title">🕐 {r['hora_inicio']}–{r['hora_fim']} &nbsp;
                    <span class="badge" style="background:{cor}20;color:{cor}">Sala {r['sala']}</span>
                </div>
                <div class="card-sub">{r['assunto']}</div>
                <div class="card-sub">👤 {r['funcionario']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhuma reunião neste dia.")


def pagina_agendar(sistema: SistemaAgendamento):
    st.title("Agendar Reunião")
    slots = gerar_slots_horario()
    nomes_salas = [s.codigo for s in sistema.salas]
    nomes_funcs = [f.nome for f in sistema.funcionarios]

    with st.form("form_agendar"):
        c1, c2 = st.columns(2)
        with c1:
            sala = st.selectbox("Sala", nomes_salas)
            data_r = st.date_input("Data", value=date.today())
        with c2:
            funcionario = st.selectbox("Responsável", nomes_funcs)
            assunto = st.text_input("Assunto")

        c3, c4 = st.columns(2)
        with c3:
            inicio = st.selectbox("Início", slots, index=4)
        with c4:
            fim_opts = slots[slots.index(inicio)+1:] if inicio in slots else slots
            fim = st.selectbox("Fim", fim_opts, index=min(2, len(fim_opts)-1))

        submitted = st.form_submit_button("✅ Agendar", use_container_width=True, type="primary")

    if submitted:
        if not assunto.strip():
            st.error("Informe o assunto da reunião.")
        else:
            ok, msg = sistema.agendar_reuniao(sala, str(data_r), inicio, fim, funcionario, assunto.strip())
            if ok:
                salvar_dados(sistema.to_dict())
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)

    # Preview da disponibilidade
    st.markdown("---")
    st.subheader("Disponibilidade das Salas")
    data_preview = st.date_input("Data para verificar", value=date.today(), key="prev_data")
    data_prev_str = str(data_preview)
    for s in sistema.salas:
        ocupacoes = [r for r in sistema.reunioes if r["sala"] == s.codigo and r["data"] == data_prev_str]
        if ocupacoes:
            horarios = " | ".join([f"{r['hora_inicio']}–{r['hora_fim']}" for r in sorted(ocupacoes, key=lambda x: x["hora_inicio"])])
            st.markdown(f'<div class="card"><div class="card-title">Sala {s.codigo} <span style="font-size:0.8rem;color:#94a3b8">({s.capacidade} lugares)</span></div><div class="card-sub">🔴 Ocupada: {horarios}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card" style="border-left-color:#5BAD72"><div class="card-title">Sala {s.codigo} <span style="font-size:0.8rem;color:#94a3b8">({s.capacidade} lugares)</span></div><div class="card-sub" style="color:#5BAD72">🟢 Livre o dia todo</div></div>', unsafe_allow_html=True)


def pagina_realocar(sistema: SistemaAgendamento):
    st.title("Realocar Reunião")
    slots = gerar_slots_horario()
    nomes_salas = [s.codigo for s in sistema.salas]

    if not sistema.reunioes:
        st.info("Nenhuma reunião cadastrada.")
        return

    reunioes_sorted = sorted(sistema.reunioes, key=lambda r: (r["data"], r["hora_inicio"]))
    opcoes = {f"{r['data']} | {r['hora_inicio']}–{r['hora_fim']} | Sala {r['sala']} | {r['assunto'][:30]}": r["id"]
              for r in reunioes_sorted}
    escolha = st.selectbox("Selecione a reunião", list(opcoes.keys()))
    reuniao_id = opcoes[escolha]
    r_atual = next((r for r in sistema.reunioes if r["id"] == reuniao_id), None)

    if r_atual:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Reunião atual</div>
            <div class="card-sub">📅 {r_atual['data']} | 🕐 {r_atual['hora_inicio']}–{r_atual['hora_fim']} | Sala {r_atual['sala']}</div>
            <div class="card-sub">📋 {r_atual['assunto']} | 👤 {r_atual['funcionario']}</div>
        </div>""", unsafe_allow_html=True)

    with st.form("form_realocar"):
        c1, c2 = st.columns(2)
        with c1:
            nova_sala = st.selectbox("Nova sala", nomes_salas,
                                     index=nomes_salas.index(r_atual["sala"]) if r_atual and r_atual["sala"] in nomes_salas else 0)
            nova_data = st.date_input("Nova data", value=datetime.strptime(r_atual["data"], "%Y-%m-%d").date() if r_atual else date.today())
        with c2:
            idx_ini = slots.index(r_atual["hora_inicio"]) if r_atual and r_atual["hora_inicio"] in slots else 0
            novo_inicio = st.selectbox("Novo início", slots, index=idx_ini)
            fim_opts = slots[slots.index(novo_inicio)+1:]
            idx_fim = fim_opts.index(r_atual["hora_fim"]) if r_atual and r_atual["hora_fim"] in fim_opts else 0
            novo_fim = st.selectbox("Novo fim", fim_opts, index=min(idx_fim, len(fim_opts)-1))

        submitted = st.form_submit_button("🔄 Realocar", use_container_width=True, type="primary")

    if submitted:
        ok, msg = sistema.realocar_reuniao(reuniao_id, nova_sala, str(nova_data), novo_inicio, novo_fim)
        if ok:
            salvar_dados(sistema.to_dict())
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def pagina_salas_livres(sistema: SistemaAgendamento):
    st.title("Salas Livres")
    st.markdown("Consulte salas disponíveis em uma data e faixa de horário.")

    slots = gerar_slots_horario()
    c1, c2, c3 = st.columns(3)
    with c1:
        data_sel = st.date_input("Data", value=date.today())
    with c2:
        inicio = st.selectbox("Início", slots, index=4)
    with c3:
        fim_opts = slots[slots.index(inicio)+1:]
        fim = st.selectbox("Fim", fim_opts, index=min(3, len(fim_opts)-1))

    if st.button("🔍 Consultar", type="primary"):
        livres = sistema.consultar_salas_livres(str(data_sel), inicio, fim)
        if livres:
            st.success(f"{len(livres)} sala(s) disponível(is) em {data_sel.strftime('%d/%m/%Y')} das {inicio} às {fim}:")
            for sala in livres:
                cor = cor_sala(sala.codigo)
                st.markdown(f"""
                <div class="card" style="border-left-color:{cor}">
                    <div class="card-title">🏷️ Sala {sala.codigo}</div>
                    <div class="card-sub">👥 Capacidade: <b>{sala.capacidade} pessoas</b> &nbsp;
                        <span class="badge" style="background:#dcfce7;color:#16a34a">🟢 Livre</span>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("Nenhuma sala disponível nesse horário.")


def pagina_pesquisa(sistema: SistemaAgendamento):
    st.title("Pesquisar Reuniões")
    nomes_salas = ["(Todas)"] + [s.codigo for s in sistema.salas]
    nomes_funcs = ["(Todos)"] + [f.nome for f in sistema.funcionarios]

    with st.form("form_pesquisa"):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_f = st.date_input("Data (opcional)", value=None)
        with c2:
            sala_f = st.selectbox("Sala", nomes_salas)
        with c3:
            func_f = st.selectbox("Funcionário", nomes_funcs)
        submitted = st.form_submit_button("🔍 Pesquisar", use_container_width=True, type="primary")

    if submitted:
        data_str = str(data_f) if data_f else None
        sala_val = None if sala_f == "(Todas)" else sala_f
        func_val = None if func_f == "(Todos)" else func_f
        resultado = sistema.pesquisar_reunioes(data=data_str, sala=sala_val, funcionario=func_val)

        st.markdown(f"**{len(resultado)} reunião(ões) encontrada(s)**")
        if resultado:
            pode_editar = st.session_state.get("perfil") == "admin"
            for r in resultado:
                cor = cor_sala(r["sala"])
                data_fmt = datetime.strptime(r["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                col_card, col_btn = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="card" style="border-left-color:{cor}">
                        <div class="card-title">📅 {data_fmt} · {r['hora_inicio']}–{r['hora_fim']}
                            <span class="badge" style="background:{cor}20;color:{cor}">Sala {r['sala']}</span>
                        </div>
                        <div class="card-sub">📋 {r['assunto']} | 👤 {r['funcionario']}</div>
                    </div>""", unsafe_allow_html=True)
                if pode_editar:
                    with col_btn:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_{r['id']}", help="Excluir reunião"):
                            ok, msg = sistema.excluir_reuniao(r["id"])
                            if ok:
                                salvar_dados(sistema.to_dict())
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Nenhuma reunião encontrada com esses critérios.")


def pagina_salas(sistema: SistemaAgendamento):
    st.title("Gerenciar Salas")

    # Listar
    st.subheader("Salas Cadastradas")
    if sistema.salas:
        cols = st.columns(min(4, len(sistema.salas)))
        for i, sala in enumerate(sistema.salas):
            with cols[i % 4]:
                cor = cor_sala(sala.codigo)
                n_reunioes = len([r for r in sistema.reunioes if r["sala"] == sala.codigo])
                st.markdown(f"""
                <div class="card" style="border-left-color:{cor};text-align:center">
                    <div style="font-size:2rem">🚪</div>
                    <div class="card-title">Sala {sala.codigo}</div>
                    <div class="card-sub">👥 {sala.capacidade} lugares</div>
                    <div class="card-sub">📋 {n_reunioes} reunião(ões)</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Remover {sala.codigo}", key=f"rem_sala_{sala.codigo}"):
                    ok, msg = sistema.remover_sala(sala.codigo)
                    if ok:
                        salvar_dados(sistema.to_dict())
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")
    st.subheader("Cadastrar Nova Sala")
    with st.form("form_sala"):
        c1, c2 = st.columns(2)
        with c1:
            cod = st.text_input("Código / Identificação (ex: 101, Auditório)")
        with c2:
            cap = st.number_input("Capacidade (pessoas)", min_value=1, max_value=500, value=10)
        submitted = st.form_submit_button("➕ Cadastrar Sala", type="primary")

    if submitted:
        if not cod.strip():
            st.error("Informe o código da sala.")
        else:
            ok, msg = sistema.cadastrar_sala(cod.strip(), int(cap))
            if ok:
                salvar_dados(sistema.to_dict())
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def pagina_funcionarios(sistema: SistemaAgendamento):
    st.title("Gerenciar Funcionários")

    # Listar
    st.subheader("Funcionários Cadastrados")
    if sistema.funcionarios:
        for f in sistema.funcionarios:
            n_reunioes = len([r for r in sistema.reunioes if r["funcionario"] == f.nome])
            col_info, col_acoes = st.columns([5, 2])
            with col_info:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">👤 {f.nome}</div>
                    <div class="card-sub">💼 {f.cargo} &nbsp;|&nbsp; 📞 Ramal: {f.ramal} &nbsp;|&nbsp; 📋 {n_reunioes} reunião(ões)</div>
                </div>""", unsafe_allow_html=True)
            with col_acoes:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"🗑️ Remover", key=f"rem_func_{f.nome}"):
                    ok, msg = sistema.remover_funcionario(f.nome)
                    if ok:
                        salvar_dados(sistema.to_dict())
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")
    st.subheader("Cadastrar / Editar Funcionário")
    nomes_existentes = ["(Novo funcionário)"] + [f.nome for f in sistema.funcionarios]
    modo = st.selectbox("Modo", nomes_existentes)

    valores_default = {"nome": "", "cargo": "", "ramal": ""}
    nome_original = None
    if modo != "(Novo funcionário)":
        f_sel = next((f for f in sistema.funcionarios if f.nome == modo), None)
        if f_sel:
            valores_default = {"nome": f_sel.nome, "cargo": f_sel.cargo, "ramal": f_sel.ramal}
            nome_original = f_sel.nome

    with st.form("form_func"):
        c1, c2, c3 = st.columns(3)
        with c1:
            nome = st.text_input("Nome completo", value=valores_default["nome"])
        with c2:
            cargo = st.text_input("Cargo", value=valores_default["cargo"])
        with c3:
            ramal = st.text_input("Ramal", value=valores_default["ramal"])
        label_btn = "💾 Salvar Alterações" if nome_original else "➕ Cadastrar"
        submitted = st.form_submit_button(label_btn, type="primary")

    if submitted:
        if not nome.strip() or not cargo.strip():
            st.error("Nome e cargo são obrigatórios.")
        else:
            ok, msg = sistema.manter_funcionario(nome.strip(), cargo.strip(), ramal.strip(), nome_original)
            if ok:
                salvar_dados(sistema.to_dict())
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="SalaSync – Agendamento de Salas",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    injetar_css()

    # Estado de autenticação
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        tela_login()
        return

    # Carregar sistema
    if "sistema" not in st.session_state:
        st.session_state["sistema"] = SistemaAgendamento(carregar_dados())

    sistema: SistemaAgendamento = st.session_state["sistema"]
    perfil = st.session_state.get("perfil", "viewer")
    usuario = st.session_state.get("usuario", "")
    eh_admin = perfil == "admin"

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0.5rem 1.5rem;">
            <div style="font-size:1.8rem;text-align:center">🏢</div>
            <h2 style="font-family:'DM Serif Display',serif;text-align:center;font-size:1.3rem;color:white!important;margin:0.3rem 0 0.2rem">SalaSync</h2>
            <p style="text-align:center;font-size:0.78rem;color:#94a3b8!important;margin:0">Sistema de Agendamento</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="color:#64748b;font-size:0.75rem;padding:0 0.5rem 0.5rem;text-transform:uppercase;letter-spacing:0.05em">Menu</div>', unsafe_allow_html=True)

        paginas_viewer = ["📊 Dashboard", "📅 Agenda do Dia", "🗓️ Agenda do Mês", "🔍 Salas Livres", "🔎 Pesquisar"]
        paginas_admin = paginas_viewer + ["➕ Agendar Reunião", "🔄 Realocar", "🚪 Salas", "👥 Funcionários"]
        paginas = paginas_admin if eh_admin else paginas_viewer

        pagina = st.radio("", paginas, label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f'<div style="font-size:0.8rem;color:#94a3b8!important;padding:0 0.5rem">👤 <b style="color:#cbd5e1!important">{usuario}</b><br><span style="font-size:0.72rem">Perfil: {perfil}</span></div>', unsafe_allow_html=True)
        if st.button("Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Renderizar página
    if "Dashboard" in pagina:
        pagina_dashboard(sistema)
    elif "Agenda do Dia" in pagina:
        pagina_agenda_dia(sistema)
    elif "Agenda do Mês" in pagina:
        pagina_agenda_mes(sistema)
    elif "Salas Livres" in pagina:
        pagina_salas_livres(sistema)
    elif "Pesquisar" in pagina:
        pagina_pesquisa(sistema)
    elif "Agendar" in pagina and eh_admin:
        pagina_agendar(sistema)
    elif "Realocar" in pagina and eh_admin:
        pagina_realocar(sistema)
    elif "Salas" in pagina and eh_admin:
        pagina_salas(sistema)
    elif "Funcionários" in pagina and eh_admin:
        pagina_funcionarios(sistema)
    else:
        pagina_dashboard(sistema)

    # Atualizar sistema na session
    st.session_state["sistema"] = sistema


if __name__ == "__main__":
    main()