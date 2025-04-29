import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configurar o Streamlit para usar o modo wide
st.set_page_config(layout="wide")

# Conexão com o banco de dados
conn = sqlite3.connect('contas_casa.db', check_same_thread=False)
cursor = conn.cursor()

# Criação das tabelas se não existirem
cursor.execute('''
    CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        categoria TEXT,
        responsavel TEXT,
        valor REAL NOT NULL,
        data TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS salarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        usuario TEXT NOT NULL,
        data TEXT NOT NULL
    )
''')
conn.commit()

# Funções auxiliares
def adicionar_conta(descricao, categoria, responsavel, valor, data):
    cursor.execute('INSERT INTO contas (descricao, categoria, responsavel, valor, data) VALUES (?, ?, ?, ?, ?)',
                   (descricao, categoria, responsavel, valor, data))
    conn.commit()

def listar_contas():
    cursor.execute('SELECT * FROM contas ORDER BY data DESC')
    dados = cursor.fetchall()
    colunas = ['ID', 'Descrição', 'Categoria', 'Responsável', 'Valor', 'Data']
    return pd.DataFrame(dados, columns=colunas)

def total_gasto():
    cursor.execute('SELECT SUM(valor) FROM contas')
    total = cursor.fetchone()[0]
    return total if total else 0

def adicionar_salario(valor, usuario, data):
    cursor.execute('INSERT INTO salarios (valor, usuario, data) VALUES (?, ?, ?)', (valor, usuario, data,))
    conn.commit()

def total_salario():
    cursor.execute('SELECT SUM(valor) FROM salarios')
    total = cursor.fetchone()[0]
    return total if total else 0

def listar_salarios():
    cursor.execute('SELECT * FROM salarios ORDER BY data DESC')
    dados = cursor.fetchall()
    colunas = ['ID', 'Valor', 'usuario', 'Data']
    return pd.DataFrame(dados, columns=colunas)

# Layout do Streamlit
st.title('🏠 Dashboard de Contas de Casa')

menu = st.sidebar.selectbox("Menu", ["Cadastrar Conta", "Visualizar Contas", "Cadastrar Salário", "Resumo"])

if menu == "Cadastrar Conta":
    st.subheader("Cadastrar Nova Conta")

    with st.form(key='form_conta'):
        descricao = st.text_input("Descrição")
        categoria = st.selectbox("Categoria", ["Alimentação", "Cartão de Crédito", "Educação", "Impostos e Taxas", "Lazer", "Moradia", "Serviços de Comunicação", "Transporte", "Outros"])
        responsavel = st.selectbox("Responsável", ["Geovani", "Amanda", "Juntos"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        data = st.date_input("Data", value=datetime.today())
        botao = st.form_submit_button("Cadastrar")

        if botao:
            if descricao and valor > 0:
                adicionar_conta(descricao, categoria, responsavel, valor, data.strftime('%Y-%m-%d'))
                st.success("✅ Conta cadastrada com sucesso!")
            else:
                st.error("❌ Preencha todos os campos corretamente.")

elif menu == "Visualizar Contas":
    st.subheader("Contas Cadastradas")
    df = listar_contas()

    responsavel_filtro = st.selectbox("Filtrar por Responsável", ["Todos"] + df['Responsável'].unique().tolist())
    if responsavel_filtro != "Todos":
        df = df[df['Responsável'] == responsavel_filtro]

    st.dataframe(df, use_container_width=True)

elif menu == "Cadastrar Salário":
    st.subheader("Cadastrar Novo Salário")

    with st.form(key='form_salario'):
        valor_salario = st.number_input("Valor do Salário (R$)", min_value=0.0, step=0.01)
        usuario = st.selectbox("Usuário", ["Geovani", "Amanda"])
        data_salario = st.date_input("Data de Recebimento", value=datetime.today())
        botao_salario = st.form_submit_button("Cadastrar Salário")

        if botao_salario:
            if valor_salario > 0:
                adicionar_salario(valor_salario, usuario, data_salario.strftime('%Y-%m-%d'))
                st.success("✅ Salário cadastrado com sucesso!")
            else:
                st.error("❌ Preencha o valor corretamente.")

elif menu == "Resumo":
    st.subheader("Resumo Financeiro")

    df = listar_contas()

    if not df.empty:
        df['Data'] = pd.to_datetime(df['Data'])
        df['AnoMes'] = df['Data'].dt.to_period('M').astype(str)

        data_hoje = datetime.today()
        mes_atual = data_hoje.month
        ano_atual = data_hoje.year

        ano_selecionado = st.selectbox("Ano:", sorted(df['Data'].dt.year.unique(), reverse=True), index=0)
        mes_selecionado = st.selectbox("Mês:", sorted(df[df['Data'].dt.year == ano_selecionado]['Data'].dt.month.unique()))

        df_cards = df[(df['Data'].dt.month == mes_selecionado) & (df['Data'].dt.year == ano_selecionado)]

        responsaveis = ["Todos"] + df['Responsável'].unique().tolist()
        responsavel_selecionado = st.selectbox("Filtrar Resumo por Responsável:", responsaveis)
        if responsavel_selecionado != "Todos":
            df_cards = df_cards[df_cards['Responsável'] == responsavel_selecionado]

        total = df_cards['Valor'].sum()
        
        # Filtrando salários pelo período selecionado
        df_salarios = listar_salarios()
        df_salarios['Data'] = pd.to_datetime(df_salarios['Data'])
        df_salarios_filtrado = df_salarios[
            (df_salarios['Data'].dt.month == mes_selecionado) & 
            (df_salarios['Data'].dt.year == ano_selecionado)
        ]
        salario = df_salarios_filtrado['Valor'].sum()
        saldo = salario - total

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💸 Total Gasto", f"R$ {total:,.2f}")
        with col2:
            st.metric("💰 Total Salário", f"R$ {salario:,.2f}")
        with col3:
            st.metric("📈 Saldo Atual", f"R$ {saldo:,.2f}", delta="↑" if saldo >= 0 else "↓")

        if saldo < 0:
            st.error("🚨 Alerta: Seu saldo atual está negativo!")

        st.markdown("---")
        st.subheader("Análises Visuais")

        # Usando df_cards para os resumos do período selecionado
        resumo_responsavel = df_cards.groupby('Responsável')['Valor'].sum().reset_index()
        resumo_categoria = df_cards.groupby('Categoria')['Valor'].sum().reset_index()
        resumo_mensal = df_cards.groupby('AnoMes')['Valor'].sum().reset_index()

        col4, col5 = st.columns(2)

        with col4:
            st.subheader("Gastos por Responsável")
            st.bar_chart(resumo_responsavel.set_index('Responsável'))

        with col5:
            st.subheader("Gastos por Categoria")
            st.bar_chart(resumo_categoria.set_index('Categoria'))

        col6, col7 = st.columns(2)

        with col6:
            st.subheader("Gastos Mensais")
            meses_selecionados = st.multiselect("Filtrar Meses:", resumo_mensal['AnoMes'].unique(), default=resumo_mensal['AnoMes'].unique())
            filtro_mensal = resumo_mensal[resumo_mensal['AnoMes'].isin(meses_selecionados)]
            st.line_chart(filtro_mensal.set_index('AnoMes'))

        with col7:
            st.subheader("Comparativo Salário vs Gastos")
            # Usando df_salarios_filtrado para o comparativo
            df_salarios_filtrado['AnoMes'] = df_salarios_filtrado['Data'].dt.to_period('M').astype(str)
            resumo_salario_mensal = df_salarios_filtrado.groupby('AnoMes')['Valor'].sum().reset_index()
            comparativo = pd.merge(resumo_salario_mensal, resumo_mensal, on='AnoMes', how='outer').fillna(0)
            comparativo = comparativo.rename(columns={'Valor_x': 'Salário', 'Valor_y': 'Gastos'})
            comparativo = comparativo.set_index('AnoMes')
            st.line_chart(comparativo)

        st.markdown("---")
        st.subheader("Tabela de Economia Mensal")

        comparativo['% Economia'] = ((comparativo['Salário'] - comparativo['Gastos']) / comparativo['Salário']) * 100
        comparativo['% Economia'] = comparativo['% Economia'].fillna(0)

        def cor_economia(val):
            color = 'green' if val >= 0 else 'red'
            return f'color: {color}'

        st.dataframe(
            comparativo[['Salário', 'Gastos', '% Economia']]
            .style.format({
                'Salário': 'R$ {:,.2f}',
                'Gastos': 'R$ {:,.2f}',
                '% Economia': '{:.2f}%'
            }).applymap(cor_economia, subset=['% Economia'])
        )

    else:
        st.info("Nenhuma conta cadastrada ainda.")
