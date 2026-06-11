import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configurando a página
st.set_page_config(page_title="Dashboard Violações", layout="wide")

# 2. Carregando a base de dados
df = pd.read_excel('denuncias-2023-2025.xlsx')

# 3. Criando um filtro lateral
#add_selectbox = st.sidebar.selectbox(
#    'How would you like to be contacted?',
#    ('Email', 'Home phone', 'Mobile phone')
#)

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
col3, col4, col5 = st.columns(3)

col1.metric("Total de Denuncias", total_denuncias)
col2.metric("Total Violações", total_violacoes)

# === CRIAR GRÁFICO DE VIOLAÇÕES POR BAIRRO ===

# 1. Agrupar os dados filtrados (usa .size() e renomeia a coluna gerada para 'quantidade')
df_agrupado = (
    df.groupby(['bairro_da_vítima', 'tipo_de_violência_denunciada'], as_index=False)
    .size()
    .rename(columns={'size': 'quantidade'})
)


# 2. Criar a lista do ranking baseada nos dados filtrados
# O gráfico é horizontal, para o maior ficar em cima, ordenação aqui deve ser Ascendente (True)
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

# 3. Criar o gráfico com o DataFrame agrupado direto
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


# Força o eixo Y a obedecer à ordem matemática calculada
fig_violacoes_bairro.update_yaxes(categoryorder='array', categoryarray=ranking_bairros)

# Ajuste de layout 
fig_violacoes_bairro.update_layout(height=max(400, len(ranking_bairros) * 30))

fig_violacoes_bairro.update_xaxes(range=[0, 30])


# Exibindo na coluna correspondente
col3.plotly_chart(fig_violacoes_bairro, use_container_width=True)

# === CRIAR GRÁFICO DE DENUNCIAS E VIOLAÇÕES POR ANO ===

col_data = 'data' 

# 2. Extrair o número do mês (1 a 12) e o nome do mês abreviado/completo
df['mes_num'] = df[col_data].dt.month
df['mes_nome'] = df[col_data].dt.strftime('%b') # %b gera 'Jan', 'Fev'

# meses sempre em português, mapeamento manual alternativo:
#mapa_meses = {
#    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
#    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
#}
#df['mes_nome'] = df['mes_num'].map(mapa_meses)

# 3. Agrupar os dados por número e nome do mês para manter a ordem cronológica correta
df_evolucao_mes = (
    df.groupby(['mes_num', 'mes_nome'], as_index=False)['protocolo']
    .nunique()
    .rename(columns={'protocolo': 'Total_Denuncias'})
    .sort_values('mes_num') #ordenação
)

# 4. Criar o gráfico de linha usando o nome do mês no eixo X
fig_linha_evolucao = px.line(
    df_evolucao_mes,
    x='mes_nome',
    y='Total_Denuncias',
    title='Evolução das Denúncias por Mês',
    markers=True,
    labels={'mes_nome': 'Mês', 'Total_Denuncias': 'Qtd. Denúncias'}
)

col4.plotly_chart(fig_linha_evolucao, use_container_width=True)

# col5: GRÁFICO DE PIRÂMIDE - FAIXA ETÁRIA E GÊNERO
# ==============================================================================

#minhas colunas
col_idade = 'faixa_etária' 
col_genero = 'sexo'

# 1. Agrupar por idade e gênero
df_piramide = df.groupby([col_idade, col_genero], as_index=False).size().rename(columns={'size': 'quantidade'})

# 2. identificar os gêneros
generos = df_piramide[col_genero].unique()

fig_piramide = go.Figure()

if len(generos) >= 2:
    # feminino - Valores normais para a direita
    df_g1 = df_piramide[df_piramide[col_genero] == generos[0]]
    fig_piramide.add_trace(go.Bar(
        y=df_g1[col_idade],
        x=df_g1['quantidade'],
        name=str(generos[0]),
        orientation='h',
        marker_color='lightcoral',    
        text=df_g1['quantidade'],              # Define o dado que vira rótulo
        texttemplate='%{text}',                 # Formato simples do texto
        textposition='outside'                  # Posição: fora da barra (mude para 'inside' se preferir)
    ))

    # Masculino - Valores negativos para a esquerda
    df_g2 = df_piramide[df_piramide[col_genero] == generos[1]]
    fig_piramide.add_trace(go.Bar(
        y=df_g2[col_idade],
        x=df_g2['quantidade'] * -1, # Multiplica por -1 para ir para a esquerda
        name=str(generos[1]),
        orientation='h',
        text=df_g2['quantidade'],              # Define o dado que vira rótulo
        texttemplate='%{text}',                 # Formato simples do texto
        textposition='outside'                  # Posição: fora da barra (mude para 'inside' se preferir)
    ))

 # 3. Ajuste dinâmico dos eixos com base no seu volume
    max_valor = int(df_piramide['quantidade'].max()) if not df_piramide.empty else 300
    # Arredonda para a próxima centena para dar margem visual no gráfico
    limite_eixo = ((max_valor // 100) + 1) * 100 
    passo = limite_eixo // 4 # Divide o eixo em 4 intervalos limpos

    # Cria as marcações negativas para a esquerda e positivas para a direita
    valores_ticks = list(range(-limite_eixo, limite_eixo + 1, passo))
    textos_ticks = [str(abs(x)) for x in valores_ticks] # Remove o sinal de menos (-) do texto visual

    fig_piramide.update_layout(
        title='Violações por Faixa Etária e Gênero',
        barmode='overlay', 
        height=450,
        xaxis=dict(
            title='Quantidade de Violações',
            tickmode='array',
            tickvals=valores_ticks,
            ticktext=textos_ticks,
            range=[-limite_eixo, limite_eixo] # Força limites idênticos nos dois lados
        ),
        yaxis=dict(
            title='Faixa Etária'
        )
    )

col5.plotly_chart(fig_piramide, use_container_width=True)