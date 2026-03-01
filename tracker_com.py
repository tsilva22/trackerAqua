import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from datetime import datetime
import time

# --- CONFIGURAÇÃO E MOTOR DE BUSCA ---
dict_tickers = {
    "Milho": "CORN", 
    "Soja": "SOYB", 
    "Trigo": "WEAT",
    "Farelo Soja": "ZM=F",  # Contrato Futuro contínuo de Farelo
    "Óleo Soja": "ZL=F",    # Contrato Futuro contínuo de Óleo
    "Petróleo (Brent)": "BZ=F", # Importante para custo de frete
    "Açúcar": "CANE",
    "Dólar": "USDBRL=X"
}

# ttl=3600 significa que ele só vai na internet 1 vez por hora (evita ban de IP)
@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados_yf(ticker):
    try:
        # Busca 1 ano de dados
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(period="1y")
        
        if not data.empty:
            df = data[['Close']].reset_index()
            # Garante que a coluna Date seja datetime e Close seja float
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            df['Close'] = df['Close'].astype(float)
            return df
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return None
    return None

# --- INTERFACE ---
st.set_page_config(page_title="AgroTicker: Intelligence", layout="wide", page_icon="🐟")
st.title("🐟 AgroTicker Analytics")
st.markdown("Dashboard estratégico com proteção de cache contra bloqueios de IP.")
with st.expander("ℹ️ Nota sobre a disponibilidade dos dados"):
    st.info("""
    Este dashboard utiliza a API pública do Yahoo Finance. 
    Devido a restrições de IP em servidores de nuvem (Streamlit Cloud), o carregamento dos dados 
    pode sofrer instabilidades temporárias. 
    
    **Caso os gráficos não carreguem:**
    1. Tente clicar no botão **Resetar Dados** na barra lateral.
    2. Atualize a página (F5).
    3. Consulte os prints no [Repositório do GitHub](SEU_LINK_AQUI) para visualizar a interface funcional.
    """)

# --- SIDEBAR ---
st.sidebar.header("🛡️ Parâmetros")
unidade_sel = st.sidebar.selectbox("Unidade de Medida:", 
    ["R$ / Tonelada (Brasil)", "R$ / Saca 60kg (Brasil)", "US$ / Bushel (Chicago)", "US$ / Tonelada (Global)"])

insumos_disponiveis = [k for k in dict_tickers.keys() if k != "Dólar"]
insumos_selecionados = st.sidebar.multiselect(
    "Filtrar Insumos:",
    options=insumos_disponiveis,
    default=insumos_disponiveis
)
janela = st.sidebar.slider("Janela de Visualização (Dias):", 7, 180, 60)

if st.sidebar.button("♻️ Forçar Atualização de Dados"):
    st.cache_data.clear()
    st.rerun()

# --- PROCESSAMENTO ---
with st.spinner('Lendo dados do cache (Proteção de IP ativa)...'):
    dados_hist = {}
    for nome, tk in dict_tickers.items():
        dados_hist[nome] = buscar_dados_yf(tk)
        # Pequena pausa entre requisições apenas na primeira vez (quando não há cache)
        # time.sleep(0.5) 

# Lógica do Dólar
df_dolar = dados_hist.get('Dólar')
dolar_atual = float(df_dolar['Close'].iloc[-1]) if isinstance(df_dolar, pd.DataFrame) else 5.25

# Lógica de Conversão
def converter(valor_usd, nome, unidade):
    if "R$ / Tonelada" in unidade:
        f = 39.36 if nome == "Milho" else 36.74
        return float(valor_usd) * dolar_atual * f
    if "R$ / Saca" in unidade:
        f = 2.36 if nome == "Milho" else 2.20
        return float(valor_usd) * dolar_atual * f
    if "US$ / Tonelada" in unidade:
        f = 39.36 if nome == "Milho" else 36.74
        return float(valor_usd) * f
    return float(valor_usd)

# --- MÉTRICAS ---
st.subheader(f"📊 Mercado em Tempo Real ({unidade_sel})")
cols = st.columns(len(insumos_disponiveis))

for i, nome in enumerate(insumos_disponiveis):
    with cols[i]:
        res = dados_hist.get(nome)
        if isinstance(res, pd.DataFrame) and not res.empty:
            v_atual = converter(res['Close'].iloc[-1], nome, unidade_sel)
            v_ant = converter(res['Close'].iloc[-2], nome, unidade_sel)
            st.metric(nome, f"{v_atual:,.2f}", f"{((v_atual/v_ant)-1)*100:.2f}%")
        else:
            st.error(f"{nome} offline")

# --- INTELIGÊNCIA ---
stats_data = []
insights = []
comp_list = []

for nome in insumos_selecionados:
    df = dados_hist.get(nome)
    if isinstance(df, pd.DataFrame) and not df.empty:
        temp = df.copy()
        temp['Preco_Ajustado'] = temp.apply(lambda x: converter(x['Close'], nome, unidade_sel), axis=1)
        temp['SMA_15'] = temp['Preco_Ajustado'].rolling(window=15).mean()
        temp['Insumo'] = nome
        comp_list.append(temp.tail(janela))

        precos = temp['Preco_Ajustado'].tail(janela)
        v_atual = precos.iloc[-1]
        v_media = precos.mean()
        volatilidade = (precos.std() / v_media) * 100
        
        stats_data.append({
            "Insumo": nome,
            "Média": f"{v_media:,.2f}",
            "Volatilidade": f"{volatilidade:.2f}%",
            "Status": "🔴 Alta" if volatilidade > 5 else "🟢 Estável"
        })

        if v_atual > v_media * 1.05:
            insights.append(f"⚠️ **{nome}**: Alta de {((v_atual/v_media)-1)*100:.1f}% vs média.")
        elif v_atual < v_media * 0.95:
            insights.append(f"✅ **{nome}**: Oportunidade (abaixo da média).")

# --- ABAS ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📈 Tendências & Insights", "🧬 Análise de Correlação", "📋 Dados Brutos"])

with tab1:
    col_graph, col_info = st.columns([3, 1])
    with col_graph:
        if comp_list:
            df_grafico = pd.concat(comp_list)
            base = alt.Chart(df_grafico).encode(x=alt.X('Date:T', title=None), color='Insumo:N')
            lines = base.mark_line(strokeWidth=3, interpolate='monotone').encode(
                y=alt.Y('Preco_Ajustado:Q', scale=alt.Scale(zero=False), title="Preço"),
                tooltip=['Insumo', 'Date', 'Preco_Ajustado']
            )
            st.altair_chart(lines.properties(height=450).interactive(bind_y=False), width='stretch')
        else:
            st.info("Selecione insumos para visualizar o gráfico.")
    
    with col_info:
        st.subheader("Resumo")
        for n in insights: st.info(n)
        if not insights: st.write("Preços operando na média.")
        st.markdown("---")
        st.write("**Volatilidade**")
        if stats_data:
            st.dataframe(pd.DataFrame(stats_data).set_index("Insumo"))

with tab2:
    st.subheader("🧬 Matriz de Correlação")
    st.markdown("Entenda como os preços se movem em conjunto.")
    df_corr_list = []
    for n in insumos_disponiveis:
        if isinstance(dados_hist[n], pd.DataFrame):
            df_temp = dados_hist[n][['Date', 'Close']].rename(columns={'Close': n}).set_index('Date')
            df_corr_list.append(df_temp)
    
    if len(df_corr_list) > 1:
        df_final_corr = pd.concat(df_corr_list, axis=1).dropna()
        corr_matrix = df_final_corr.corr().reset_index().melt(id_vars='index')
        corr_matrix.columns = ['I1', 'I2', 'Corr']
        
        heatmap = alt.Chart(corr_matrix).mark_rect().encode(
            x='I1:N', y='I2:N', 
            color=alt.Color('Corr:Q', scale=alt.Scale(scheme='viridis')),
            tooltip=['I1', 'I2', 'Corr']
        ).properties(height=450)
        
        st.altair_chart(heatmap, width='stretch')

with tab3:
    if comp_list:
        st.dataframe(pd.concat(comp_list).sort_values(by='Date', ascending=False), width='stretch')

st.caption(f"Dólar Ref: R$ {dolar_atual:.2f} | Cache expira em 1h | {datetime.now().strftime('%H:%M:%S')}")