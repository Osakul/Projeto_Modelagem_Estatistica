import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="Análise IBGE - Modelagem Estatística", initial_sidebar_state="expanded")
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'figure.autolayout': True})


# 1. Carregar os Dados
@st.cache_data
def load_data():
    # Lê o CSV que está na mesma pasta. O delimitador é ';'
    df = pd.read_csv('base_dashboard_final.csv', sep=';', encoding='latin1')
    return df

df = load_data()

# 2. Painel Lateral - Filtros
st.sidebar.header("Filtros Exploratórios")

anos_estudo = st.sidebar.slider(
    "Nível Máximo de Escolaridade (Anos)", 
    min_value=int(df['Anos_Estudo_Max'].min()), 
    max_value=int(df['Anos_Estudo_Max'].max()), 
    value=(0, 24)
)

moradores = st.sidebar.multiselect(
    "Qtd. de Moradores",
    options=sorted(df['Qtd_Moradores'].unique()),
    default=sorted(df['Qtd_Moradores'].unique())[:5]
)

# Aplicar filtros

#df_filtered = df[
#    (df['Anos_Estudo_Max'] >= anos_estudo[0]) & 
#    (df['Anos_Estudo_Max'] <= anos_estudo[1]) &
#    (df['Qtd_Moradores'].isin(moradores))
#]

if not moradores:
    df_filtered = df[
        (df['Anos_Estudo_Max'] >= anos_estudo[0]) & 
        (df['Anos_Estudo_Max'] <= anos_estudo[1])
    ]
else:
    df_filtered = df[
        (df['Anos_Estudo_Max'] >= anos_estudo[0]) & 
        (df['Anos_Estudo_Max'] <= anos_estudo[1]) &
        (df['Qtd_Moradores'].isin(moradores))
    ]

# 3. KPIs
col1, col2, col3, col4 = st.columns(4)

# Checagem: O filtro encontrou alguma coisa?
if df_filtered.empty:
    col1.metric("Média da Renda Per Capita (R$)", "Sem dados")
    col2.metric("Total de Domicílios Analisados", "0")
    col3.metric("R² do Modelo (OLS)", "-")
    col4.metric("Validade (P-valor)", "-")
    st.divider()
    st.warning("Nenhum domicílio encontrado com esta combinação de filtros. Tente selecionar um intervalo de escolaridade maior ou outras quantidades de moradores.")

else:
    # Se encontrou dados, mostra os KPIs normalmente
    renda_media = df_filtered['D0360'].mean()
    col1.metric("Renda Per Capita Média", f"R$ {renda_media:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Total Analisado", f"{len(df_filtered):,}".replace(",", "."))
    col3.metric("R² do Modelo (OLS)", "7.4%")
    col4.metric("Validade Geral (P-valor)", "< 0.001")
    st.divider()

    # 4. Gráficos (Só desenha se houver dados)
    colA, colB = st.columns(2)

    with colA:
        fig_scatter, ax_scatter = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=df_filtered, x='Anos_Estudo_Max', y='D0360', alpha=0.3, s=25, edgecolor=None, color='#2c7bb6', ax=ax_scatter)
        ax_scatter.set_title("Escolaridade vs Renda")
        ax_scatter.set_ylabel("Renda Per Capita")
        ax_scatter.set_xlabel("Anos de Estudo Máximo")
        sns.despine(left=True)
        st.pyplot(fig_scatter)

    with colB:
        fig_box, ax_box = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df_filtered, x='Ocorreu_Obito', y='D0360', width=0.4, palette="Set2", fliersize=3, ax=ax_box)
        ax_box.set_title("Renda vs Ocorrência de Óbito")
        ax_box.set_xticklabels(['Sem Óbito', 'Com Óbito'])
        ax_box.set_ylabel("Renda Per Capita")
        ax_box.set_xlabel("")
        sns.despine(left=True)
        st.pyplot(fig_box)

    fig_bar, ax_bar = plt.subplots(figsize=(12, 4))
    df_agg = df_filtered.groupby('Qtd_Moradores')['D0360'].mean().reset_index()
    sns.barplot(data=df_agg, x='Qtd_Moradores', y='D0360', color='steelblue', edgecolor='w', ax=ax_bar)
    ax_bar.set_title("Impacto da Coabitação na Renda")
    ax_bar.set_ylabel("Média de Renda Per Capita")
    ax_bar.set_xlabel("Qtd. Moradores no Domicílio")
    sns.despine(left=True)
    st.pyplot(fig_bar)