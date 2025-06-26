#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import os
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Catálogo Musical",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.title("🎵 Catálogo Musical Interativo")

# Carregar lista de arquivos CSV
def listar_arquivos_csv():
    return [f for f in os.listdir() if f.endswith('.csv')]

# Mostrar seletor de arquivo na sidebar
arquivos_csv = listar_arquivos_csv()
if not arquivos_csv:
    st.error("Nenhum arquivo CSV encontrado na pasta atual!")
    st.stop()

arquivo_selecionado = st.sidebar.selectbox(
    "Selecione o catálogo:",
    arquivos_csv,
    index=0
)

# Carregar dados do CSV selecionado (com cache)
@st.cache_data
def load_data(arquivo_csv):
    try:
        # Carregar o CSV garantindo tratamento de tipos
        df = pd.read_csv(
            arquivo_csv, 
            delimiter='|', 
            encoding='utf-8', 
            skipinitialspace=True,
            dtype={
                'numero': str,
                'titulo': str,
                'artista': str,
                'album': str,
                'duracao': str
            }
        )
        
        # Preencher valores nulos com string vazia
        df = df.fillna('')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

data = load_data(arquivo_selecionado)

if data is None:
    st.error(f"Falha ao carregar o arquivo: {arquivo_selecionado}")
    st.stop()

# Filtros na barra lateral
st.sidebar.header("🔍 Filtros")

# Filtro por número
numero_filtro = st.sidebar.text_input("Filtrar por Número:")
# Filtro por artista
artista_filtro = st.sidebar.text_input("Filtrar por Artista:")
# Filtro por título
titulo_filtro = st.sidebar.text_input("Filtrar por Título:")
# Filtro por álbum
album_filtro = st.sidebar.text_input("Filtrar por Álbum:")

# Aplicar filtros
filtered_data = data

# Função segura para filtragem
def aplicar_filtro(df, coluna, filtro):
    if not filtro:
        return df
    
    try:
        # Para coluna numérica, converter para string
        if coluna == 'numero' and df[coluna].dtype != str:
            df[coluna] = df[coluna].astype(str)
            
        return df[df[coluna].str.contains(filtro, case=False, na=False)]
    except Exception as e:
        st.error(f"Erro ao filtrar por {coluna}: {e}")
        return df

if numero_filtro:
    filtered_data = aplicar_filtro(filtered_data, 'numero', numero_filtro)
if artista_filtro:
    filtered_data = aplicar_filtro(filtered_data, 'artista', artista_filtro)
if titulo_filtro:
    filtered_data = aplicar_filtro(filtered_data, 'titulo', titulo_filtro)
if album_filtro:
    filtered_data = aplicar_filtro(filtered_data, 'album', album_filtro)

# Mostrar dados
st.subheader(f"🎧 Músicas Encontradas: {len(filtered_data)}")

# Exibir como tabela ou cards
visualizacao = st.radio("Visualização:", ['Tabela', 'Cards'], horizontal=True)

if visualizacao == 'Tabela':
    st.dataframe(filtered_data)
else:
    for _, row in filtered_data.iterrows():
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        ">
            <h4>#{row['numero']} {row['titulo']}</h4>
            <p><b>Artista:</b> {row['artista']}</p>
            <p><b>Álbum:</b> {row['album']}</p>
            <p><b>Duração:</b> {row['duracao']}</p>
        </div>
        """, unsafe_allow_html=True)

# Opção para baixar resultados filtrados
if st.button("Baixar Resultados Filtrados"):
    filtered_data.to_csv('resultados_filtrados.csv', index=False, sep='|', encoding='utf-8')
    st.success("Arquivo 'resultados_filtrados.csv' gerado com sucesso!")
    with open('resultados_filtrados.csv', 'rb') as f:
        st.download_button(
            label="Clique para baixar",
            data=f,
            file_name='resultados_filtrados.csv',
            mime='text/csv'
        )