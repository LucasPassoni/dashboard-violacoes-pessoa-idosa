import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configurando a página
st.set_page_config(page_title="Dashboard Violações", layout="wide")

# 2. Carregando a base de dados
df = pd.read_excel('denuncias-2023-2025.xlsx')

# 3. Criando um filtro lateral (Sidebar)
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

st.sidebar.header("Filtros")
anos_disponiveis = sorted(df['ano'].unique())
ano_selecionado = st.sidebar.selectbox("Selecione o ano:", ['Todos'] + anos_disponiveis)

bairros_disponiveis = sorted(df['bairro_da_vítima'].unique())
bairro_selecionado = st.sidebar.selectbox("Selecione o bairro:", ['Todos'] + bairros_disponiveis)

# Aplicando os filtros dinamicamente
if ano_selecionado != 'Todos': 
    df = df[df['ano'] == ano_selecionado]

if bairro_selecionado != 'Todos': 
    df = df[df['bairro_da_vítima'] == bairro_selecionado]

# 5. Cálculo métricas
total_denuncias = df["protocolo"].nunique()
total_violacoes = df["protocolo"].count()

# 6. Exibindo métricas e gráficos
st.subheader("Visão Geral")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

col1.metric("Total de Denuncias", total_denuncias)
col2.metric("Total Violações", total_violacoes)

# === CRIAR GRÁFICO DE VIOLAÇÕES POR BAIRRO ===

# 1. Agrupar os dados filtrados (usa .size() e renomeia a coluna gerada para 'quantidade')
df_agrupado = (
    df.groupby(['bairro_da_vítima', 'tipo_de_violência_denunciada'], as_index=False)
    .size()
    .rename(columns={'size': 'quantidade'})
)


# 2. Criar a lista do RANKING baseada estritamente nos dados que sobraram pós-filtro
# O gráfico é horizontal, para o maior ficar no TOPO, a ordenação aqui deve ser Ascendente (True)
# pois o eixo Y do Plotly começa a desenhar de baixo para cima.
ranking_bairros = (
    df_agrupado.groupby('bairro_da_vítima')['quantidade']
    .sum()
    .sort_values(ascending=True)
    .tail(10)
    .index
    .tolist()
)

#filtro para plotar apenas os bairros que estão no ranking. 
df_grafico_filtrado = df_agrupado[df_agrupado['bairro_da_vítima'].isin(ranking_bairros)]

# 3. Criar o gráfico com o DataFrame agrupado direto (sem necessidade de merge)
fig_violacoes_bairro = px.bar(
    df_grafico_filtrado,
    x='quantidade', 
    y='bairro_da_vítima', 
    title='Violações por Bairro', 
    orientation="h", 
    color='tipo_de_violência_denunciada', 
    barmode='group',
    labels={'quantidade': 'Total de Violações', 'bairro_da_vítima': 'Bairro', 'tipo_de_violência_denunciada': 'Tipo de Violação'}
)


# CORREÇÃO: Força o eixo Y a obedecer rigorosamente à ordem matemática calculada
fig_violacoes_bairro.update_yaxes(categoryorder='array', categoryarray=ranking_bairros)

# Ajuste de layout para melhor leitura caso existam muitos bairros
fig_violacoes_bairro.update_layout(height=max(400, len(ranking_bairros) * 30))

fig_violacoes_bairro.update_xaxes(range=[0, 30])


# Exibindo na coluna correspondente
col3.plotly_chart(fig_violacoes_bairro, use_container_width=True)

# === CRIAR GRÁFICO DE DENUNCIAS E VIOLAÇÕES POR ANO ===

# 1. Agrupar os dados por ano
df_evolucao = df.groupby('data', as_index=False)['protocolo'].nunique().rename(columns={'protocolo': 'Total_Denuncias'})

# 2. Criar o gráfico de linha
fig_linha_evolucao = px.line(
    df_evolucao,
    x='data',
    y='Total_Denuncias',
    title='Evolução das Denúncias ao Longo dos Anos',
    markers=True, # Adiciona pontinhos na linha
    labels={'data': 'Data', 'Total_Denuncias': 'Qtd. Denúncias'}
)

# Ajustes visuais na linha
fig_linha_evolucao.update_traces(line=dict(width=3), marker=dict(size=8))
fig_linha_evolucao.update_layout(height=450, xaxis=dict(dtick=1)) # dtick=1 força mostrar ano a ano sem decimais

col4.plotly_chart(fig_linha_evolucao, use_container_width=True)

