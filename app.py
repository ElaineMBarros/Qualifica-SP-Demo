
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Dashboard de Cursos", layout="wide")

@st.cache_data
def carregar_dados():
    return pd.read_csv("base_cursos_tratada.csv", parse_dates=["data_inicio"])

df = carregar_dados()

st.title("📊 Dashboard de Cursos Ativos")

# Filtros
col1, col2, col3, col4 = st.columns(4)
cidade = col1.multiselect("Cidade", df['municipio'].unique(), default=None)
curso = col2.multiselect("Curso", df['curso'].unique(), default=None)
modalidade = col3.multiselect("Modalidade", df['modalidade'].unique(), default=None)
formato = col4.multiselect("Formato", df['formato'].unique(), default=None)

df_filtrado = df.copy()
if cidade:
    df_filtrado = df_filtrado[df_filtrado['municipio'].isin(cidade)]
if curso:
    df_filtrado = df_filtrado[df_filtrado['curso'].isin(curso)]
if modalidade:
    df_filtrado = df_filtrado[df_filtrado['modalidade'].isin(modalidade)]
if formato:
    df_filtrado = df_filtrado[df_filtrado['formato'].isin(formato)]

# Métricas
st.metric("Total de Turmas", len(df_filtrado))
st.metric("Total de Vagas Disponíveis", int(df_filtrado['vagas_disponiveis'].sum()))
st.metric("Média da Carga Horária", round(df_filtrado['carga_horaria'].mean(), 2))

# Gráficos com os 20 maiores
st.subheader("📍 Top 20 Municípios com Mais Turmas")
turmas_por_cidade = df_filtrado['municipio'].value_counts().sort_values(ascending=False).head(20)
fig_cidade, ax_cidade = plt.subplots(figsize=(10, 5))
bars = ax_cidade.bar(turmas_por_cidade.index, turmas_por_cidade.values)
ax_cidade.set_ylabel("Quantidade de Turmas")
ax_cidade.set_xlabel("Município")
plt.xticks(rotation=45, ha='right', fontsize=8)
for bar in bars:
    height = bar.get_height()
    ax_cidade.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                       textcoords="offset points", ha='center', va='bottom', fontsize=8)
fig_cidade.tight_layout()
st.pyplot(fig_cidade)

st.subheader("📚 Top 20 Cursos com Mais Turmas")
turmas_por_curso = df_filtrado['curso'].value_counts().sort_values(ascending=False).head(20)
fig_curso, ax_curso = plt.subplots(figsize=(12, 5))
bars = ax_curso.bar(turmas_por_curso.index, turmas_por_curso.values)
ax_curso.set_ylabel("Quantidade de Turmas")
ax_curso.set_xlabel("Curso")
plt.xticks(rotation=60, ha='right', fontsize=8)
for bar in bars:
    height = bar.get_height()
    ax_curso.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                      textcoords="offset points", ha='center', va='bottom', fontsize=8)
fig_curso.tight_layout()
st.pyplot(fig_curso)

# Gráficos lado a lado
st.subheader("📅 Datas de Início e Distribuição das Turmas")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("**Datas de Início das Turmas**")
    datas_inicio = df_filtrado['data_inicio'].dt.date.value_counts().sort_index()
    fig_datas, ax_datas = plt.subplots(figsize=(8, 4))
    bars = ax_datas.bar(datas_inicio.index.astype(str), datas_inicio.values)
    ax_datas.set_ylabel("Quantidade de Turmas")
    ax_datas.set_xlabel("Data de Início")
    plt.xticks(rotation=45, ha='right', fontsize=8)
    for bar in bars:
        height = bar.get_height()
        ax_datas.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                          textcoords="offset points", ha='center', va='bottom', fontsize=8)
    fig_datas.tight_layout()
    st.pyplot(fig_datas)

with col_g2:
    st.markdown("**Distribuição das Turmas por Modalidade**")
    modalidade_counts = df_filtrado['modalidade'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.pie(modalidade_counts, labels=modalidade_counts.index, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    ax2.axis('equal')
    st.pyplot(fig2)

# Botão para download da base filtrada
st.subheader("📥 Download dos Dados Filtrados")
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='CursosFiltrados')
    writer.save()
st.download_button label="📄 Baixar Excel com Dados Filtrados",
                   data=buffer.getvalue(),
                   file_name="cursos_filtrados.xlsx",
                   mime="application/vnd.openxmlformats