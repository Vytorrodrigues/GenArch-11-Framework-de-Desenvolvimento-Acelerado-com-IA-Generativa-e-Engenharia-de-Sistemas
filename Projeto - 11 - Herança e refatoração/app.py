import streamlit as st


# =========================
# MODELO ORIENTADO A OBJETOS
# =========================
class Pessoa:
    def __init__(self, nome: str, cpf: str, email: str, telefone: str):
        self.nome = nome.strip()
        self.cpf = cpf.strip()
        self.email = email.strip()
        self.telefone = telefone.strip()

    def tipo(self) -> str:
        return "Pessoa"

    def dados_gerais(self) -> dict:
        return {
            "Tipo": self.tipo(),
            "Nome": self.nome,
            "CPF": self.cpf,
            "E-mail": self.email,
            "Telefone": self.telefone,
        }

    def resumo(self) -> str:
        return f"{self.tipo()} | {self.nome} | CPF: {self.cpf}"


class Cliente(Pessoa):
    def __init__(
        self,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        codigo_cliente: str,
        endereco: str,
        limite_credito: float,
    ):
        super().__init__(nome, cpf, email, telefone)
        self.codigo_cliente = codigo_cliente.strip()
        self.endereco = endereco.strip()
        self.limite_credito = float(limite_credito)

    def tipo(self) -> str:
        return "Cliente"

    def dados_especificos(self) -> dict:
        return {
            "Código do Cliente": self.codigo_cliente,
            "Endereço": self.endereco,
            "Limite de Crédito": f"R$ {self.limite_credito:,.2f}",
        }

    def dados_completos(self) -> dict:
        dados = self.dados_gerais()
        dados.update(self.dados_especificos())
        return dados


class Funcionario(Pessoa):
    def __init__(
        self,
        nome: str,
        cpf: str,
        email: str,
        telefone: str,
        matricula: str,
        cargo: str,
        salario: float,
    ):
        super().__init__(nome, cpf, email, telefone)
        self.matricula = matricula.strip()
        self.cargo = cargo.strip()
        self.salario = float(salario)

    def tipo(self) -> str:
        return "Funcionário"

    def dados_especificos(self) -> dict:
        return {
            "Matrícula": self.matricula,
            "Cargo": self.cargo,
            "Salário": f"R$ {self.salario:,.2f}",
        }

    def dados_completos(self) -> dict:
        dados = self.dados_gerais()
        dados.update(self.dados_especificos())
        return dados


# =========================
# FUNÇÕES DE APOIO
# =========================
def inicializar_estado():
    if "lista_geral" not in st.session_state:
        st.session_state.lista_geral = []

    if "clientes" not in st.session_state:
        st.session_state.clientes = []

    if "funcionarios" not in st.session_state:
        st.session_state.funcionarios = []


def aplicar_estilo():
    st.set_page_config(
        page_title="Sistema de Herança - Usuários",
        page_icon="👥",
        layout="wide",
    )

    st.markdown(
        """
        <style>
            .titulo-principal {
                font-size: 2rem;
                font-weight: 700;
                color: #1f4e79;
                margin-bottom: 0.3rem;
            }
            .subtitulo {
                font-size: 1rem;
                color: #444;
                margin-bottom: 1rem;
            }
            .caixa-info {
                background-color: #0e1117;
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid #dbe2ea;
                margin-bottom: 1rem;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )


def validar_campos_basicos(nome, cpf, email, telefone) -> list:
    erros = []

    if not nome.strip():
        erros.append("O nome é obrigatório.")
    if not cpf.strip():
        erros.append("O CPF é obrigatório.")
    if not email.strip():
        erros.append("O e-mail é obrigatório.")
    if not telefone.strip():
        erros.append("O telefone é obrigatório.")

    return erros


def cpf_ja_cadastrado(cpf: str) -> bool:
    for pessoa in st.session_state.lista_geral:
        if pessoa.cpf == cpf.strip():
            return True
    return False


def cadastrar_cliente(nome, cpf, email, telefone, codigo_cliente, endereco, limite_credito):
    erros = validar_campos_basicos(nome, cpf, email, telefone)

    if not codigo_cliente.strip():
        erros.append("O código do cliente é obrigatório.")
    if not endereco.strip():
        erros.append("O endereço é obrigatório.")
    if limite_credito < 0:
        erros.append("O limite de crédito não pode ser negativo.")
    if cpf_ja_cadastrado(cpf):
        erros.append("Já existe uma pessoa cadastrada com este CPF.")

    if erros:
        return False, erros

    cliente = Cliente(
        nome=nome,
        cpf=cpf,
        email=email,
        telefone=telefone,
        codigo_cliente=codigo_cliente,
        endereco=endereco,
        limite_credito=limite_credito,
    )

    st.session_state.lista_geral.append(cliente)
    st.session_state.clientes.append(cliente)

    return True, ["Cliente cadastrado com sucesso."]


def cadastrar_funcionario(nome, cpf, email, telefone, matricula, cargo, salario):
    erros = validar_campos_basicos(nome, cpf, email, telefone)

    if not matricula.strip():
        erros.append("A matrícula é obrigatória.")
    if not cargo.strip():
        erros.append("O cargo é obrigatório.")
    if salario < 0:
        erros.append("O salário não pode ser negativo.")
    if cpf_ja_cadastrado(cpf):
        erros.append("Já existe uma pessoa cadastrada com este CPF.")

    if erros:
        return False, erros

    funcionario = Funcionario(
        nome=nome,
        cpf=cpf,
        email=email,
        telefone=telefone,
        matricula=matricula,
        cargo=cargo,
        salario=salario,
    )

    st.session_state.lista_geral.append(funcionario)
    st.session_state.funcionarios.append(funcionario)

    return True, ["Funcionário cadastrado com sucesso."]


def exibir_card_pessoa(pessoa):
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Tipo:** {pessoa.tipo()}")
        st.write(f"**Nome:** {pessoa.nome}")
        st.write(f"**CPF:** {pessoa.cpf}")
        st.write(f"**E-mail:** {pessoa.email}")

    with col2:
        st.write(f"**Telefone:** {pessoa.telefone}")

        if isinstance(pessoa, Cliente):
            st.write(f"**Código do Cliente:** {pessoa.codigo_cliente}")
            st.write(f"**Endereço:** {pessoa.endereco}")
            st.write(f"**Limite de Crédito:** R$ {pessoa.limite_credito:,.2f}")

        elif isinstance(pessoa, Funcionario):
            st.write(f"**Matrícula:** {pessoa.matricula}")
            st.write(f"**Cargo:** {pessoa.cargo}")
            st.write(f"**Salário:** R$ {pessoa.salario:,.2f}")


def exibir_resumo_quantitativo():
    total = len(st.session_state.lista_geral)
    total_clientes = len(st.session_state.clientes)
    total_funcionarios = len(st.session_state.funcionarios)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Geral", total)
    col2.metric("Clientes", total_clientes)
    col3.metric("Funcionários", total_funcionarios)


def tela_cadastro():
    st.subheader("Cadastro de Usuários com Herança")
    st.markdown(
        """
        <div class="caixa-info">
            Nesta tela, a classe <strong>Pessoa</strong> centraliza os atributos em comum
            e as subclasses <strong>Cliente</strong> e <strong>Funcionario</strong> armazenam
            apenas os dados específicos de cada perfil.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_cadastro"):
        tipo_usuario = st.selectbox(
            "Selecione o tipo de cadastro",
            ["Cliente", "Funcionário"]
        )

        st.markdown("### Dados Gerais da Pessoa")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            cpf = st.text_input("CPF")
        with col2:
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone")

        st.markdown("### Dados Específicos")

        if tipo_usuario == "Cliente":
            col3, col4 = st.columns(2)
            with col3:
                codigo_cliente = st.text_input("Código do Cliente")
                endereco = st.text_input("Endereço")
            with col4:
                limite_credito = st.number_input(
                    "Limite de Crédito",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f"
                )

        else:
            col3, col4 = st.columns(2)
            with col3:
                matricula = st.text_input("Matrícula")
                cargo = st.text_input("Cargo")
            with col4:
                salario = st.number_input(
                    "Salário",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f"
                )

        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if tipo_usuario == "Cliente":
                sucesso, mensagens = cadastrar_cliente(
                    nome=nome,
                    cpf=cpf,
                    email=email,
                    telefone=telefone,
                    codigo_cliente=codigo_cliente,
                    endereco=endereco,
                    limite_credito=limite_credito,
                )
            else:
                sucesso, mensagens = cadastrar_funcionario(
                    nome=nome,
                    cpf=cpf,
                    email=email,
                    telefone=telefone,
                    matricula=matricula,
                    cargo=cargo,
                    salario=salario,
                )

            if sucesso:
                for msg in mensagens:
                    st.success(msg)
            else:
                for msg in mensagens:
                    st.error(msg)


def tela_lista_geral():
    st.subheader("Lista Geral de Instâncias")
    exibir_resumo_quantitativo()

    if not st.session_state.lista_geral:
        st.info("Nenhum registro cadastrado até o momento.")
        return

    filtro_tipo = st.selectbox(
        "Filtrar visualização",
        ["Todos", "Cliente", "Funcionário"]
    )

    pessoas_filtradas = []
    for pessoa in st.session_state.lista_geral:
        if filtro_tipo == "Todos":
            pessoas_filtradas.append(pessoa)
        elif filtro_tipo == "Cliente" and isinstance(pessoa, Cliente):
            pessoas_filtradas.append(pessoa)
        elif filtro_tipo == "Funcionário" and isinstance(pessoa, Funcionario):
            pessoas_filtradas.append(pessoa)

    st.write(f"**Total exibido:** {len(pessoas_filtradas)}")

    for pessoa in pessoas_filtradas:
        exibir_card_pessoa(pessoa)


def tela_clientes():
    st.subheader("Subpainel de Clientes")

    if not st.session_state.clientes:
        st.info("Nenhum cliente cadastrado.")
        return

    busca = st.text_input("Pesquisar cliente por nome")
    clientes_filtrados = []

    for cliente in st.session_state.clientes:
        if busca.strip().lower() in cliente.nome.lower():
            clientes_filtrados.append(cliente)

    st.write(f"**Quantidade de clientes encontrados:** {len(clientes_filtrados)}")

    for cliente in clientes_filtrados:
        exibir_card_pessoa(cliente)


def tela_funcionarios():
    st.subheader("Subpainel de Funcionários")

    if not st.session_state.funcionarios:
        st.info("Nenhum funcionário cadastrado.")
        return

    busca = st.text_input("Pesquisar funcionário por nome")
    funcionarios_filtrados = []

    for funcionario in st.session_state.funcionarios:
        if busca.strip().lower() in funcionario.nome.lower():
            funcionarios_filtrados.append(funcionario)

    st.write(f"**Quantidade de funcionários encontrados:** {len(funcionarios_filtrados)}")

    for funcionario in funcionarios_filtrados:
        exibir_card_pessoa(funcionario)


def tela_relatorio():
    st.subheader("Relatório Unificado")

    if not st.session_state.lista_geral:
        st.info("Não há dados para compor o relatório.")
        return

    st.markdown("### Visão Consolidada")
    for pessoa in st.session_state.lista_geral:
        dados = pessoa.dados_gerais()

        if isinstance(pessoa, Cliente):
            dados.update(pessoa.dados_especificos())
        elif isinstance(pessoa, Funcionario):
            dados.update(pessoa.dados_especificos())

        st.json(dados)


def main():
    aplicar_estilo()
    inicializar_estado()

    st.markdown('<div class="titulo-principal">Sistema de Herança de Usuários</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitulo">Modelagem orientada a objetos com superclasse Pessoa e subclasses Cliente e Funcionario.</div>',
        unsafe_allow_html=True
    )

    abas = st.tabs(
        [
            "Cadastro",
            "Lista Geral",
            "Clientes",
            "Funcionários",
            "Relatório",
        ]
    )

    with abas[0]:
        tela_cadastro()

    with abas[1]:
        tela_lista_geral()

    with abas[2]:
        tela_clientes()

    with abas[3]:
        tela_funcionarios()

    with abas[4]:
        tela_relatorio()


if __name__ == "__main__":
    main()