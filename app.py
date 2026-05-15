import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# =========================================
# CONFIG
# =========================================

st.set_page_config(
    page_title="Institutional Terminal PRO",
    layout="wide"
)

# =========================================
# CSS
# =========================================

st.markdown("""
<style>
.main {
    background-color: #020817;
    color: white;
}

.stMetric {
    background-color: #071226;
    padding: 10px;
    border-radius: 10px;
}

h1,h2,h3,h4 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# DADOS MANUAIS
# =========================================
# Aqui você pode depois ligar API ou yfinance

dados = [
    {"Ativo": "VALE3", "Variacao": -2.86},
    {"Ativo": "PETR4", "Variacao": 0.16},
    {"Ativo": "ITUB4", "Variacao": -0.97},
    {"Ativo": "BBDC4", "Variacao": -1.29},
    {"Ativo": "BBSE3", "Variacao": -0.38},
    {"Ativo": "WEGE3", "Variacao": -0.59},
    {"Ativo": "SMLL", "Variacao": -2.16},
]

# =========================================
# PESOS REAIS DO IBOV
# =========================================

pesos = {
    "VALE3": 0.12,
    "PETR4": 0.11,
    "ITUB4": 0.08,
    "BBDC4": 0.06,
    "BBSE3": 0.02,
    "WEGE3": 0.02,
    "SMLL": 0.03,
}

# =========================================
# CONTEXTO MACRO
# =========================================

DXY = 0.29
EWZ = -2.96
WDOFUT = 1.30

# =========================================
# DATAFRAME
# =========================================

df = pd.DataFrame(dados)

# =========================================
# CALCULAR IMPACTO
# =========================================

impactos = []

for _, row in df.iterrows():

    ativo = row["Ativo"]
    variacao = row["Variacao"]

    peso = pesos.get(ativo, 0)

    impacto = variacao * peso * 100

    impactos.append(impacto)

df["Impacto"] = impactos

# =========================================
# SCORE BASE
# =========================================

score_ibov = df["Impacto"].sum()

# =========================================
# AJUSTE MACRO
# =========================================

macro_score = 0

# DXY subindo = ruim para bolsa
macro_score -= DXY * 50

# EWZ caindo = estrangeiro vendendo
macro_score += EWZ * 10

# dólar futuro subindo forte = pressão
macro_score -= WDOFUT * 10

score_final = score_ibov + macro_score

# =========================================
# CLASSIFICAÇÃO
# =========================================

if score_final >= 40:
    sinal = "🟢 Compra Forte"

elif score_final >= 10:
    sinal = "🟢 Compra Moderada"

elif score_final <= -40:
    sinal = "🔴 Venda Forte"

elif score_final <= -10:
    sinal = "🔴 Venda Moderada"

else:
    sinal = "⚪ Neutro"

# =========================================
# HEADER
# =========================================

st.title("🏦 Institutional Terminal PRO")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("WIN SCORE", round(score_final, 2))
col2.metric("DXY", f"{DXY}%")
col3.metric("EWZ", f"{EWZ}%")
col4.metric("WDOFUT", f"{WDOFUT}%")
col5.metric("Atualização", datetime.now().strftime("%H:%M"))

# =========================================
# SINAL
# =========================================

if "Compra" in sinal:
    st.success(sinal)

elif "Venda" in sinal:
    st.error(sinal)

else:
    st.warning(sinal)

# =========================================
# GAUGE
# =========================================

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score_final,

    title={'text': "WIN SCORE"},

    gauge={
        'axis': {'range': [-100, 100]},

        'bar': {'color': "white"},

        'steps': [
            {'range': [-100, -40], 'color': "darkred"},
            {'range': [-40, -10], 'color': "red"},
            {'range': [-10, 10], 'color': "gray"},
            {'range': [10, 40], 'color': "green"},
            {'range': [40, 100], 'color': "darkgreen"},
        ]
    }
))

fig.update_layout(
    paper_bgcolor="#04122b",
    font={'color': "white"},
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# =========================================
# TABELA
# =========================================

st.subheader("📊 Impacto Real no Índice")

df = df.sort_values(by="Impacto")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================
# GRÁFICO
# =========================================

fig2 = go.Figure()

cores = []

for valor in df["Impacto"]:

    if valor > 0:
        cores.append("green")
    else:
        cores.append("red")

fig2.add_trace(go.Bar(
    x=df["Impacto"],
    y=df["Ativo"],
    orientation='h',
    marker_color=cores
))

fig2.update_layout(
    paper_bgcolor="#04122b",
    plot_bgcolor="#04122b",
    font=dict(color="white"),
    title="Peso Real no IBOV",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)