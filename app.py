# =========================================================
# INSTITUTIONAL TERMINAL PRO 5.0
# WIN + WDO + SETORES + ETF + CURVA DE JUROS
# =========================================================

# INSTALAR:
# pip install streamlit plotly pandas yfinance streamlit-autorefresh

# EXECUTAR:
# streamlit run app.py

# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=3000, key="refresh")

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Terminal PRO",
    layout="wide",
    page_icon="📈"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #050816;
    color: white;
}

.main {
    background-color: #050816;
}

.block-container {
    padding-top: 1rem;
}

div[data-testid="metric-container"] {
    background-color: #0d1425;
    border: 1px solid #1c2940;
    padding: 15px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TÍTULO
# =========================================================

st.title("🏦 Institutional Terminal PRO")

# =========================================================
# IBOV
# =========================================================

IBOV = 146787

# =========================================================
# PESOS
# =========================================================

pesos = {

    "VALE3.SA": 0.1101,
    "PETR4.SA": 0.0830,
    "PETR3.SA": 0.0470,
    "ITUB4.SA": 0.0836,
    "BBDC4.SA": 0.0366,
    "WEGE3.SA": 0.0263,
    "BBAS3.SA": 0.0248,
    "PRIO3.SA": 0.0176,
}

# =========================================================
# SETORES
# =========================================================

setores = {

    "IFNC": 1.19,
    "IMAT": 0.26,
    "IMOB": 1.61,
    "ICON": 0.98,
    "SMLL": 1.42,
    "UTIL": 0.20
}

# =========================================================
# ETFS
# =========================================================

etfs = {

    "EWZ": 5,
    "SPY": 4,
    "QQQ": 4,
    "XLF": 3,
    "XLE": 4,
    "EEM": 4
}

# =========================================================
# CLASSIFICAÇÃO
# =========================================================

def classificar(valor):

    if valor >= 8:
        return "🟢 Compra Forte"

    elif valor >= 2:
        return "🟡 Compra"

    elif valor <= -8:
        return "🔴 Venda Forte"

    elif valor <= -2:
        return "🟠 Venda"

    else:
        return "⚪ Neutro"

# =========================================================
# FUNÇÃO
# =========================================================

def pegar_dados(ticker):

    try:

        ativo = yf.Ticker(ticker)

        hist = ativo.history(
            period="1d",
            interval="5m"
        )

        if len(hist) < 2:
            return None

        close = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]

        open_day = hist["Open"].iloc[0]

        var_5m = (
            (
                close - prev
            ) / prev
        ) * 100

        var_day = (
            (
                close - open_day
            ) / open_day
        ) * 100

        momentum = var_day - var_5m

        return {

            "var_5m": round(var_5m,2),
            "var_day": round(var_day,2),
            "momentum": round(momentum,2)
        }

    except:

        return None

# =========================================================
# ENGINE AÇÕES
# =========================================================

dados_acoes = []

score_win = 0
score_wdo = 0

impacto_total = 0

for ticker, peso in pesos.items():

    info = pegar_dados(ticker)

    if info is None:
        continue

    impacto = (
        IBOV *
        peso *
        (
            info["var_day"] / 100
        )
    )

    sentimento = (
        info["momentum"]
        * peso
        * 100
    )

    impacto_total += impacto

    score_win += sentimento

    status = classificar(sentimento)

    dados_acoes.append({

        "Ativo": ticker.replace(".SA",""),
        "Peso %": round(peso * 100,2),
        "Dia %": info["var_day"],
        "5min %": info["var_5m"],
        "Momentum": info["momentum"],
        "Impacto": round(impacto,2),
        "Sentimento": round(sentimento,2),
        "Status": status
    })

# =========================================================
# DATAFRAME
# =========================================================

df_acoes = pd.DataFrame(dados_acoes)

# =========================================================
# SETORES
# =========================================================

dados_setores = []

for nome, valor in setores.items():

    score = valor * 4

    score_win += score

    dados_setores.append({

        "Setor": nome,
        "Variação %": valor,
        "Força": round(score,2),
        "Status": classificar(score)
    })

df_setores = pd.DataFrame(dados_setores)

# =========================================================
# ETF FLOW
# =========================================================

dados_etf = []

for etf, peso in etfs.items():

    try:

        ativo = yf.Ticker(etf)

        hist = ativo.history(period="1d")

        close = hist["Close"].iloc[-1]
        open_price = hist["Open"].iloc[0]

        variacao = (
            (
                close - open_price
            ) / open_price
        ) * 100

        score = variacao * peso

        score_win += score

        dados_etf.append({

            "ETF": etf,
            "Variação %": round(variacao,2),
            "Força": round(score,2),
            "Status": classificar(score)
        })

    except:

        pass

df_etf = pd.DataFrame(dados_etf)

# =========================================================
# CURVA DE JUROS
# =========================================================

curva = {

    "DI1F26": -0.07,
    "DI1F27": -0.14,
    "DI1F28": -0.36,
    "DI1F29": -0.57,
    "DI1F31": -0.50
}

dados_di = []

for nome, valor in curva.items():

    dados_di.append({

        "DI": nome,
        "Variação %": valor,
        "Status": classificar(valor * 20)
    })

df_di = pd.DataFrame(dados_di)

# =========================================================
# DXY
# =========================================================

try:

    dxy = yf.Ticker("DX-Y.NYB")

    hist = dxy.history(period="1d")

    close = hist["Close"].iloc[-1]
    open_price = hist["Open"].iloc[0]

    dxy_var = (
        (
            close - open_price
        ) / open_price
    ) * 100

except:

    dxy_var = 0

# =========================================================
# SCORE FINAL
# =========================================================

if dxy_var > 0:

    score_win -= 15
    score_wdo += 15

else:

    score_win += 15
    score_wdo -= 15

# =========================================================
# STATUS FINAL
# =========================================================

status_win = classificar(score_win)
status_wdo = classificar(score_wdo)

# =========================================================
# TOPO
# =========================================================

top1, top2, top3, top4, top5 = st.columns(5)

with top1:
    st.metric(
        "WIN SCORE",
        round(score_win,2)
    )

with top2:
    st.metric(
        "WDO SCORE",
        round(score_wdo,2)
    )

with top3:
    st.metric(
        "DXY",
        f"{round(dxy_var,2)}%"
    )

with top4:
    st.metric(
        "Impacto IBOV",
        f"{round(impacto_total)} pts"
    )

with top5:
    st.metric(
        "Atualização",
        datetime.now().strftime("%H:%M")
    )

# =========================================================
# STATUS
# =========================================================

s1, s2 = st.columns(2)

with s1:
    st.success(f"WIN → {status_win}")

with s2:
    st.warning(f"WDO → {status_wdo}")

# =========================================================
# GAUGES
# =========================================================

g1, g2 = st.columns(2)

with g1:

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=score_win,

        title={'text': "WIN SCORE"},

        gauge={

            'axis': {'range': [-100,100]},

            'bar': {'color': "lime"},

            'steps': [

                {'range': [-100,-30], 'color': "#5a0000"},
                {'range': [-30,0], 'color': "#884400"},
                {'range': [0,30], 'color': "#444400"},
                {'range': [30,100], 'color': "#003b1f"}
            ]
        }
    ))

    fig.update_layout(
        paper_bgcolor="#0d1425",
        font_color="white",
        height=350
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with g2:

    fig2 = go.Figure(go.Indicator(

        mode="gauge+number",

        value=score_wdo,

        title={'text': "WDO SCORE"},

        gauge={

            'axis': {'range': [-100,100]},

            'bar': {'color': "red"},

            'steps': [

                {'range': [-100,-30], 'color': "#003b1f"},
                {'range': [-30,0], 'color': "#444400"},
                {'range': [0,30], 'color': "#884400"},
                {'range': [30,100], 'color': "#5a0000"}
            ]
        }
    ))

    fig2.update_layout(
        paper_bgcolor="#0d1425",
        font_color="white",
        height=350
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# AÇÕES
# =========================================================

st.subheader("📊 Sentimento das Ações")

fig3 = px.bar(

    df_acoes.sort_values("Sentimento"),

    x="Sentimento",
    y="Ativo",

    orientation="h",

    color="Sentimento",

    text="Status",

    hover_data=[

        "Dia %",
        "5min %",
        "Momentum"
    ],

    height=500
)

fig3.update_layout(

    paper_bgcolor="#0d1425",
    plot_bgcolor="#0d1425",
    font_color="white"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================================
# SETORES
# =========================================================

st.subheader("🏦 Força Setorial")

fig4 = px.bar(

    df_setores,

    x="Setor",
    y="Força",

    color="Força",

    text="Status",

    hover_data=["Variação %"],

    height=400
)

fig4.update_layout(

    paper_bgcolor="#0d1425",
    plot_bgcolor="#0d1425",
    font_color="white"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =========================================================
# ETF FLOW
# =========================================================

st.subheader("🌍 ETF FLOW")

fig5 = px.bar(

    df_etf,

    x="ETF",
    y="Força",

    color="Força",

    text="Status",

    hover_data=["Variação %"],

    height=400
)

fig5.update_layout(

    paper_bgcolor="#0d1425",
    plot_bgcolor="#0d1425",
    font_color="white"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# =========================================================
# CURVA DE JUROS
# =========================================================

st.subheader("📈 Curva de Juros")

fig6 = go.Figure()

fig6.add_trace(go.Scatter(

    x=df_di["DI"],
    y=df_di["Variação %"],

    mode='lines+markers+text',

    text=df_di["Status"],

    textposition="top center"
))

fig6.update_layout(

    paper_bgcolor="#0d1425",
    plot_bgcolor="#0d1425",
    font_color="white",

    height=500
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# =========================================================
# TABELAS
# =========================================================

t1, t2 = st.columns(2)

with t1:

    st.subheader("📋 Ações")

    st.dataframe(
        df_acoes,
        use_container_width=True
    )

with t2:

    st.subheader("📋 Setores / ETF / DI")

    st.dataframe(
        df_setores,
        use_container_width=True
    )

    st.dataframe(
        df_etf,
        use_container_width=True
    )

    st.dataframe(
        df_di,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("""
Institutional Terminal PRO 5.0
WIN + WDO + ETF FLOW + CURVA DE JUROS
""")