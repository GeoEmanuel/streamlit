import streamlit as st
import pandas as pd
from pandas import read_excel
import plotly.express as px

# Título 
st.title('Dashboard')

# Subtítulo
st.write('O arquivo deve conter as seguintes colunas "Data" e "Cadastro"')

# Botão de escolher arquivo
arquivo = st.file_uploader("Escolha seu arquivo em *EXCEL*", type=['xlsx'])


# Exibindo a previsão
st.subheader('Previsão para os próximos meses')

# Se o arquivo não existir faça
if arquivo is not None:
    # Tenta ler o arquivo Excel enviado pelo usuário
    try:
        df = read_excel(arquivo)
        
        # Verifica se as colunas "ds" e "y" estão presentes no DataFrame
        if 'Data' in df.columns and 'Cadastro' in df.columns:
            
            # Se as colunas estiverem presentes, cria um gráfico de linha com a coluna "Data" como índice
            # Grafico de linha
            fig = px.line(df, x='Data', y='Cadastro', title='Gráfico de Linhas Interativo')
            st.plotly_chart(fig)
            
            # Cria um gráfico de barras com a coluna "Data" como índice e os valores da coluna "Criação"
            # Grafico de Barras
            st.bar_chart(df.set_index('Data')['Cadastro'])
            
        else:
            # Exibe uma mensagem de erro se as colunas "ds" e "y" não estiverem presentes
            st.error("O arquivo deve conter as colunas 'Data' e 'Cadastro'")
    except Exception as e:
        # Exibe uma mensagem de erro se ocorrer algum problema ao ler o arquivo
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    # Exibe uma mensagem de aviso se nenhum arquivo foi enviado
    st.warning("Sem arquivo")



