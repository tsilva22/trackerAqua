# 🐟 AgroTicker: Monitor de Commodities para Nutrição Aquícola

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)] https://trackeraqua-8pwtjrsxb8b6ftrvwovvku.streamlit.app/

Sistema inteligente para monitoramento estratégico de insumos, desenvolvido para suporte à decisão na indústria de nutrição animal. O projeto automatiza a coleta, tratamento e visualização de dados de bolsas globais (CBOT/CME), normalizando-os para a realidade do mercado brasileiro.

## 🚀 Funcionalidades Técnicas

* **Data Pipeline Robusto:** Extração automatizada de séries temporais via API `yfinance`.
* **Camada de Cache:** Implementação de `st.cache_data` para otimização de performance e mitigação de bloqueios de IP (Rate Limiting).
* **Normalização Cambial e de Unidades:**
    * Conversão dinâmica USD/BRL em tempo real.
    * Transformação de *US cents/Bushel* para *BRL/Tonelada* utilizando constantes de massa específica (Milho: 25.401kg | Soja: 27.215kg).
* **Analytics & BI:** * Matriz de correlação dinâmica para análise de risco e interdependência de insumos.
    * Cálculo de volatilidade industrial e alertas automáticos de desvio de média.
* **Visualização Avançada:** Gráficos interativos com `Altair`, otimizados para evidenciar tendências diárias.

## 🛠 Stack Tecnológica

* **Linguagem:** Python 3.11+
* **Interface:** Streamlit
* **Data Science:** Pandas (ETL) e Altair (Visualização)
* **Data Source:** Yahoo Finance API

## 📊 Lógica de Negócio (Conversão)

O sistema utiliza a seguinte equação para precificação em moeda local:
$$Preço_{Ton} = \left(\frac{Cotação_{CBOT}}{100}\right) \times Câmbio \times Fator_{Conversão}$$

## 👤 Desenvolvedora

**Thaís Oliveira, Ph.D.** Engenheira de Pesca e Doutora em Aquicultura pela UNESP. Especialista em nutrição animal e coautora de softwares registrados no INPI.

---
*Este projeto demonstra a interseção entre ciência animal e engenharia de dados.*