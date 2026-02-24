import yfinance as yf
import pandas as pd
import streamlit as st
import altair as alt

# Função para buscar dados históricos
def buscar_dados_completos(ticker):
    try:
        ativo = yf.Ticker(ticker)
        df = ativo.history(period="60d")
        if not df.empty:
            df = df.reset_index()
            return df
        return None
    except Exception:
        return None

# Configuração da Interface
st.set_page_config(page_title="AgroTicker Pro", layout="wide")
st.title("🐟 Monitor de Commodities para Aquicultura")

# --- Sidebar (Menu Lateral) ---
st.sidebar.header("Configurações")
unidade = st.sidebar.radio("Selecione a Unidade de Exibição:", 
                           ("Global (US cents/Bushel)", "Brasil (R$/Tonelada)"))

st.sidebar.markdown("---")
st.sidebar.info("Dashboard focado em commodities de bolsa para composição de custo de ração.")

dict_tickers = {
    "Milho": "ZC=F",
    "Soja": "ZS=F",
    "Óleo de Soja": "ZL=F",
    "Farelo de Soja": "ZM=F",
    "Aveia": "ZO=F",
    "Dolar": "USDBRL=X"
}

# Busca de dados
with st.spinner('Atualizando cotações do mercado...'):
    dados_hist = {nome: buscar_dados_completos(tk) for nome, tk in dict_tickers.items()}

# Valor do dólar
dolar = dados_hist['Dolar']['Close'].iloc[-1] if dados_hist['Dolar'] is not None else 5.18

# --- Seção 1: Métricas Principais ---
st.subheader("🌾 Principais Insumos (Cotações Atuais)")
cols = st.columns(len(dados_hist) - 1)

for i, (nome, df) in enumerate(dados_hist.items()):
    if nome == "Dolar": continue
    
    col = cols[i]
    if df is not None:
        v_atual = df['Close'].iloc[-1]
        v_ant = df['Close'].iloc[-2]
        delta = v_atual - v_ant
        
        if unidade == "Global (US cents/Bushel)":
            col.metric(nome, f"{v_atual:.2f}", f"{delta:.2f}")
        else:
            fator = 39.368 if nome == "Milho" else 36.744
            v_ton = (v_atual / 100) * dolar * fator
            d_ton = (delta / 100) * dolar * fator
            col.metric(nome, f"R$ {v_ton:.2f}/T", f"{d_ton:.2f}")
    else:
        col.error(f"{nome}: N/A")

# --- Seção 2: Gráficos de Tendência com Altair (Eixo Dinâmico) ---
st.markdown("---")
st.subheader("📈 Tendência Histórica (Eixo Focado na Variação)")

nomes_insumos = [n for n in dados_hist.keys() if n != "Dolar"]
abas = st.tabs(nomes_insumos)

for aba, nome in zip(abas, nomes_insumos):
    df = dados_hist[nome]
    with aba:
        if df is not None:
            # Criando gráfico Altair com escala dinâmica (scale=alt.Scale(domainMin=...))
            # O parâmetro 'zero=False' força o eixo a focar nos dados
            chart = alt.Chart(df).mark_line(color='#1f77b4', strokeWidth=3).encode(
                x=alt.X('Date:T', title='Data'),
                y=alt.Y('Close:Q', title='Preço $USD', scale=alt.Scale(zero=False)),
                tooltip=['Date', 'Close']
            ).properties(height=400).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning(f"Dados históricos indisponíveis para {nome}")

st.markdown("---")
st.metric("Câmbio Comercial (Referência)", f"R$ {dolar:.2f}")
st.caption("Gráficos gerados via Altair com eixo Y dinâmico para melhor visualização da volatilidade.")