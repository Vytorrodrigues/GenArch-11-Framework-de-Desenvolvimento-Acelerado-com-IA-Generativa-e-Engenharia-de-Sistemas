import streamlit as st
import json
import os
from typing import List

DATA_FILE = "data.json"

# =========================
# MODELS
# =========================

class Musico:
    def __init__(self, nome: str):
        self.nome = nome
        self.cds = []

    def to_dict(self):
        return {"nome": self.nome}

    @staticmethod
    def from_dict(data):
        return Musico(data["nome"])


class Musica:
    def __init__(self, titulo: str):
        self.titulo = titulo

    def to_dict(self):
        return {"titulo": self.titulo}

    @staticmethod
    def from_dict(data):
        return Musica(data["titulo"])


class Faixa:
    def __init__(self, ordem: int, duracao: float, musica: Musica):
        self.ordem = ordem
        self.duracao = duracao
        self.musica = musica

    def to_dict(self):
        return {
            "ordem": self.ordem,
            "duracao": self.duracao,
            "musica": self.musica.titulo
        }


class CD:
    def __init__(self, titulo: str, ano: int, coletanea: bool, duplo: bool):
        self.titulo = titulo
        self.ano = ano
        self.coletanea = coletanea
        self.duplo = duplo
        self.musicos: List[Musico] = []
        self.faixas: List[Faixa] = []

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "ano": self.ano,
            "coletanea": self.coletanea,
            "duplo": self.duplo,
            "musicos": [m.nome for m in self.musicos],
            "faixas": [f.to_dict() for f in self.faixas]
        }

    @staticmethod
    def from_dict(data, musicos_dict, musicas_dict):
        cd = CD(data["titulo"], data["ano"], data["coletanea"], data["duplo"])
        cd.musicos = [musicos_dict[n] for n in data["musicos"]]
        for f in data["faixas"]:
            musica = musicas_dict[f["musica"]]
            cd.faixas.append(Faixa(f["ordem"], f["duracao"], musica))
        return cd


class ColecaoCD:
    def __init__(self):
        self.cds: List[CD] = []
        self.musicos: List[Musico] = []
        self.musicas: List[Musica] = []

    # =====================
    # PERSISTENCE
    # =====================
    def save(self):
        data = {
            "musicos": [m.to_dict() for m in self.musicos],
            "musicas": [m.to_dict() for m in self.musicas],
            "cds": [c.to_dict() for c in self.cds]
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load():
        if not os.path.exists(DATA_FILE):
            return ColecaoCD.mock()

        with open(DATA_FILE) as f:
            data = json.load(f)

        colecao = ColecaoCD()

        musicos_dict = {}
        musicas_dict = {}

        for m in data["musicos"]:
            musico = Musico.from_dict(m)
            colecao.musicos.append(musico)
            musicos_dict[musico.nome] = musico

        for m in data["musicas"]:
            musica = Musica.from_dict(m)
            colecao.musicas.append(musica)
            musicas_dict[musica.titulo] = musica

        for c in data["cds"]:
            colecao.cds.append(CD.from_dict(c, musicos_dict, musicas_dict))

        return colecao

    @staticmethod
    def mock():
        colecao = ColecaoCD()

        m1 = Musico("Coldplay")
        m2 = Musico("Adele")

        s1 = Musica("Yellow")
        s2 = Musica("Hello")

        cd1 = CD("Parachutes", 2000, False, False)
        cd1.musicos.append(m1)
        cd1.faixas.append(Faixa(1, 4.5, s1))

        cd2 = CD("25", 2015, False, False)
        cd2.musicos.append(m2)
        cd2.faixas.append(Faixa(1, 4.8, s2))

        colecao.musicos = [m1, m2]
        colecao.musicas = [s1, s2]
        colecao.cds = [cd1, cd2]

        colecao.save()
        return colecao


# =========================
# APP STATE
# =========================

if "db" not in st.session_state:
    st.session_state.db = ColecaoCD.load()

db: ColecaoCD = st.session_state.db

# =========================
# UI
# =========================

st.title("Gerenciador de CDs")

menu = st.sidebar.selectbox("Menu", [
    "Músicos",
    "Músicas",
    "CDs",
    "Faixas",
    "Relatórios"
])

# =========================
# MUSICOS
# =========================
if menu == "Músicos":
    st.header("Cadastrar Músico")

    nome = st.text_input("Nome")

    if st.button("Cadastrar"):
        if nome:
            db.musicos.append(Musico(nome))
            db.save()
            st.success("Cadastrado")

    st.subheader("Lista")
    for m in db.musicos:
        st.write(m.nome)

# =========================
# MUSICAS
# =========================
elif menu == "Músicas":
    st.header("Cadastrar Música")

    titulo = st.text_input("Título")

    if st.button("Cadastrar Música"):
        if titulo:
            db.musicas.append(Musica(titulo))
            db.save()
            st.success("OK")

    for m in db.musicas:
        st.write(m.titulo)

# =========================
# CDS
# =========================
elif menu == "CDs":
    st.header("Cadastrar CD")

    titulo = st.text_input("Título CD")
    ano = st.number_input("Ano", 1900, 2100, 2000)
    coletanea = st.checkbox("Coletânea")
    duplo = st.checkbox("Duplo")

    selected_musicos = st.multiselect(
        "Músicos",
        [m.nome for m in db.musicos]
    )

    if st.button("Salvar CD"):
        if titulo:
            cd = CD(titulo, ano, coletanea, duplo)
            cd.musicos = [m for m in db.musicos if m.nome in selected_musicos]
            db.cds.append(cd)
            db.save()
            st.success("CD salvo")

    st.subheader("Lista CDs")
    for c in db.cds:
        st.write(f"{c.titulo} ({c.ano})")

# =========================
# FAIXAS
# =========================
elif menu == "Faixas":
    st.header("Cadastrar Faixa")

    cd_nome = st.selectbox("CD", [c.titulo for c in db.cds])
    musica_nome = st.selectbox("Música", [m.titulo for m in db.musicas])
    ordem = st.number_input("Ordem", 1)
    duracao = st.number_input("Duração", 0.1)

    if st.button("Adicionar Faixa"):
        if duracao > 0:
            cd = next(c for c in db.cds if c.titulo == cd_nome)
            musica = next(m for m in db.musicas if m.titulo == musica_nome)
            cd.faixas.append(Faixa(ordem, duracao, musica))
            db.save()
            st.success("Faixa adicionada")

    st.subheader("Listar Faixas")
    for c in db.cds:
        st.write(f"CD: {c.titulo}")
        for f in c.faixas:
            st.write(f"{f.ordem} - {f.musica.titulo} ({f.duracao})")

# =========================
# RELATORIOS
# =========================
elif menu == "Relatórios":

    st.header("CDs por músico")
    musico_nome = st.selectbox("Músico", [m.nome for m in db.musicos])

    for c in db.cds:
        if any(m.nome == musico_nome for m in c.musicos):
            st.write(c.titulo)

    st.header("CDs por música")
    musica_nome = st.selectbox("Música", [m.titulo for m in db.musicas])

    for c in db.cds:
        if any(f.musica.titulo == musica_nome for f in c.faixas):
            st.write(c.titulo)