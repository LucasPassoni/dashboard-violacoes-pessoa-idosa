import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
pd.set_option('display.max_columns', None)


# 1. Configurando a página
st.set_page_config(page_title="Dashboard Violações", layout="wide")

# 2. Carregando a base de dados
df = pd.read_excel('denuncias-2023-2025.xlsx')

print(df)
st.sidebar.header("Filtros")

#Filtro ano
anos_disponiveis = sorted(df['ano'].unique())
ano_selecionado = st.sidebar.selectbox("Selecione o ano:", ['Todos'] + anos_disponiveis)

#Filtro regiao cras
regioes_disponiveis = sorted(df['regiao_cras'].unique())
regiao_selecionada = st.sidebar.selectbox("Selecione a região CRAS :", ['Todos'] + regioes_disponiveis)

#filtro condicional para região e bairros
if regiao_selecionada == 'Todos': 
    bairros_filtrados = df['bairro_da_vítima'].unique()
    
else:
    bairros_filtrados = df[df['regiao_cras'] == regiao_selecionada]['bairro_da_vítima'].unique()

bairros_disponiveis = sorted(bairros_filtrados)
bairro_selecionado = st.sidebar.selectbox("Selecione o bairro:", ['Todos'] + bairros_disponiveis)

                             
# 3. Aplicando os filtros dinamicamente
if ano_selecionado != 'Todos': 
    df = df[df['ano'] == ano_selecionado]

if bairro_selecionado != 'Todos': 
    df = df[df['bairro_da_vítima'] == bairro_selecionado]

if regiao_selecionada != 'Todos': 
    df = df[df['regiao_cras'] == regiao_selecionada]

# 4. Cálculo métricas
total_denuncias = df["protocolo"].nunique()
total_violacoes = df["protocolo"].count()

# 5. Exibindo métricas e gráficos
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
#print(df_agrupado)

# 2. top 10 bairros eixo y
top_bairros = (
     df_agrupado.groupby('bairro_da_vítima')['quantidade']
    .sum()
    .nlargest(10)
    .sort_values(ascending=True)
    .index
    .tolist()
)

#definindo o contexto
df_grafico_filtrado = df_agrupado.copy()
total_contexto = df_grafico_filtrado['quantidade'].sum()
df_grafico_filtrado['porcentagem'] = (df_grafico_filtrado['quantidade'] / total_contexto) * 100
df_grafico_filtrado = df_grafico_filtrado.sort_values(by='porcentagem', ascending=True)

#print(total_contexto)

if bairro_selecionado != 'Todos':
    # Tipos de violência nas linhas (eixo y)

    #print(total_contexto)
    eixo_y = 'tipo_de_violência_denunciada'
    cor_barra = 'tipo_de_violência_denunciada'
    barmode_tipo = 'group' 
    sequencia_eixo_y = df_grafico_filtrado['tipo_de_violência_denunciada'].tolist()
    titulo_grafico = f'Porcentagem de Violações no Bairro {bairro_selecionado}'

    # gráfico com as variáveis dinâmicas
    fig_violacoes_bairro = px.bar(
        df_grafico_filtrado,
        x='porcentagem', 
        y=eixo_y, 
        title=titulo_grafico, 
        orientation="h", 
        color=cor_barra, 
        barmode=barmode_tipo,
        labels={
            'porcentagem': 'Porcentagem (%)', 
            'bairro_da_vítima': 'Bairro', 
            'tipo_de_violência_denunciada': 'Tipo de Violação'
        },
        text=df_grafico_filtrado['porcentagem'].round(1).astype(str) + '%',
    )

    fig_violacoes_bairro.update_yaxes(categoryorder='total ascending')
else:

    df_grafico_filtrado = df_agrupado[df_agrupado['bairro_da_vítima'].isin(top_bairros)].copy()

    #bairros no eixo y
    eixo_y = 'bairro_da_vítima'
    cor_barra = 'tipo_de_violência_denunciada'
    barmode_tipo = 'group' # Mantém o agrupamento original lado a lado para múltiplos bairros
    sequencia_eixo_y = top_bairros
    titulo_grafico = 'Top 10 Bairros: Porcentagem de Violações no Período'
    
    # Filtrar para conter os 10 bairros
    df_grafico_filtrado = df_agrupado[df_agrupado['bairro_da_vítima'].isin(top_bairros)].copy()
#    print(df_grafico_filtrado)  
    
    # Calcular a porcentagem correta com base no total atual da tela
    # escolhendo um ano específico, o total_contexto será a soma total daquele ano.
    total_contexto = df_agrupado['quantidade'].sum()
    df_grafico_filtrado['porcentagem'] = (df_grafico_filtrado['quantidade'] / total_contexto) * 100

    # gráfico com as variáveis dinâmicas
    fig_violacoes_bairro = px.bar(
        df_grafico_filtrado,
        x='porcentagem', 
        y=eixo_y, 
        title=titulo_grafico, 
        orientation="h", 
        color=cor_barra, 
        barmode=barmode_tipo,
        labels={
            'porcentagem': 'Porcentagem (%)', 
            'bairro_da_vítima': 'Bairro', 
            'tipo_de_violência_denunciada': 'Tipo de Violação'
        },
        text=df_grafico_filtrado['porcentagem'].round(1).astype(str) + '%',
    )
    # Força o eixo Y a obedecer à ordem matemática calculada
    fig_violacoes_bairro.update_yaxes(categoryorder='array', categoryarray=top_bairros)     

    # Corrige a sobreposição jogando o texto para fora da barra de forma limpa
    fig_violacoes_bairro.update_traces(textposition='outside')
    fig_violacoes_bairro.update_xaxes(autorange=True)
    
    # Ajuste de layout responsivo adaptável ao tamanho dos dados
    fig_violacoes_bairro.update_layout(
        height=max(400, len(sequencia_eixo_y) * 45))



# Exibindo na coluna correspondente
col3.plotly_chart(fig_violacoes_bairro, use_container_width=True)


# === CRIAR GRÁFICO DE DENUNCIAS E VIOLAÇÕES POR ANO ===

col_data = 'data' 

# 1. Extrair o número do mês (1 a 12) e o nome do mês abreviado/completo
df['mes_num'] = df[col_data].dt.month
df['mes_nome'] = df[col_data].dt.strftime('%b') # %b gera 'Jan', 'Fev'


# 2. Agrupar os dados por número e nome do mês para manter a ordem cronológica correta
df_evolucao_mes = (
    df.groupby(['mes_num', 'mes_nome'], as_index=False)['protocolo']
    .nunique()
    .rename(columns={'protocolo': 'Total_Denuncias'})
    .sort_values('mes_num') #ordenação
)

# 3. gráfico de linha usando o nome do mês no eixo X
fig_linha_evolucao = px.line(
    df_evolucao_mes,
    x='mes_nome',
    y='Total_Denuncias',
    title='Evolução das Denúncias por Mês',
    markers=True,
    labels={'mes_nome': 'Mês', 'Total_Denuncias': 'Qtd. Denúncias'}
)

col4.plotly_chart(fig_linha_evolucao, use_container_width=True)

#GRÁFICO DE PIRÂMIDE - FAIXA ETÁRIA E GÊNERO
# ==============================================================================

#minhas colunas
col_idade = 'faixa_etária' 
col_genero = 'sexo'

# 1. Agrupar por idade e gênero, preenchendo com zero, caso algum dos gêneros não tenha informações
df_piramide = df.groupby([col_idade, col_genero]).size().rename('quantidade').unstack(fill_value=0)
    
print(df_piramide)

#verificando se todos os gêneros preenchidos, caso não tenha informações, uma coluna com zeros será criada
generos_obrigatorios = ['Feminino', 'Masculino', 'Não informado']

for gen in generos_obrigatorios:
    if gen not in df_piramide.columns:
        df_piramide[gen] = 0

#transformando sexo em coluna novamente
df_piramide = df_piramide.reset_index().melt(
    id_vars=col_idade, 
    value_name='quantidade'
)

print(df_piramide)

        
# 2. identificar os gêneros e faixa etária
generos = df_piramide[col_genero].unique()
faixa_etaria = df_piramide[col_idade].unique()

fig_piramide = go.Figure()


if len(generos) >= 2:
    
    # feminino - Valores positivos para a direita
    df_g1 = df_piramide[df_piramide[col_genero] == generos[0]].copy()
#    print(df_g1)

    # 1. Calcula o total exclusivo do gênero 0
    total_g1 = df_g1['quantidade'].sum()
    # 2. Calcula a porcentagem para este gênero
    df_g1['porcentagem'] = (df_g1['quantidade'] / total_g1) * 100

#    print(df_g1)
    fig_piramide.add_trace(go.Bar(
        y=df_g1[col_idade],
        x=df_g1['porcentagem'],
        name=str(generos[0]),
        orientation='h',
        marker_color='lightcoral',    
        text=df_g1['porcentagem'].fillna(0),              # Define o dado que vira rótulo
        texttemplate='%{text:.1f}%',            # Formato em % do texto
        textposition='outside'                  # Posição: fora da barra
    ))

    # Masculino - Valores negativos para a esquerda
    df_g2 = df_piramide[df_piramide[col_genero] == generos[1]].copy()
    
    # 1. Calcula o total exclusivo do gênero 1
    total_g2 = df_g2['quantidade'].sum()
    # 2. Calcula a porcentagem para este gênero
    df_g2['porcentagem'] = (df_g2['quantidade'] / total_g2) * 100
    

    fig_piramide.add_trace(go.Bar(
        y=df_g2[col_idade],
        x=df_g2['porcentagem'] * -1, # Multiplica por -1 para ir para a esquerda
        name=str(generos[1]),
        orientation='h',
        text=df_g2['porcentagem'].fillna(0),              # Define o dado que vira rótulo
        texttemplate='%{text:.1f}%',            # Formato em % do texto
        textposition='outside'                  # Posição: fora da barra
    ))




# 3. Ajuste dinâmico dos eixos com base no seu volume

# Encontra a maior porcentagem registrada entre os dois gêneros, considerando que algum deles pode ser 0
#maior_porcentagem = max(df_g1['porcentagem'].max(), df_g2['porcentagem'].max())
pct_g1 = df_g1['porcentagem'].max() if ('df_g1' in locals() and not df_g1.empty) else 0
pct_g2 = df_g2['porcentagem'].max() if ('df_g2' in locals() and not df_g2.empty) else 0

maior_porcentagem = max(pct_g1, pct_g2)
# Define o limite adicionando uma folga
limite_eixo = maior_porcentagem + 20 

# Cria marcações de escala 10 em 10%
valores_ticks = list(range(-int(limite_eixo), int(limite_eixo) + 1, 10))
textos_ticks = [f"{abs(x)}%" for x in valores_ticks] # Exibe positivo e com símbolo % no rodapé


# Atualiza o layout do gráfico
fig_piramide.update_layout(
    title='Violações por Faixa Etária e Gênero',
    barmode='overlay', 
    height=450,
    xaxis=dict(
        range=[-limite_eixo, limite_eixo], # Garante simetria perfeita
        tickvals=valores_ticks,
        ticktext=textos_ticks
    )
)


col5.plotly_chart(fig_piramide, use_container_width=True)