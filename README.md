# AgroTicker: Monitor de Commodities para Formulação Aquícola

Aplicação de monitoramento de insumos para suporte à decisão na indústria de nutrição animal. O sistema automatiza a coleta de dados de bolsas globais e realiza a normalização de unidades para o mercado brasileiro.

## 🛠 Funcionalidades Técnicas

* **Pipeline de Dados**: Extração de séries temporais via API `yfinance`.
* **Processamento e Normalização**:
    * Conversão de moeda (USD/BRL) em tempo real.
    * Conversão de unidades: Transformação de *US cents/Bushel* para *BRL/Tonelada* (considerando as constantes de massa específica do milho e soja).
* **Visualização Avançada**: Gráficos dinâmicos com a biblioteca **Altair**, configurados para ignorar o valor zero no eixo Y (zoom dinâmico), evidenciando a volatilidade diária.
* **Hibridismo de Fontes**: Interface que permite a inserção de benchmarks manuais para subprodutos animais sem cotação em bolsa.

## 💻 Stack Tecnológica

* **Linguagem**: Python 3.11+.
* **Bibliotecas**: `Pandas` (ETL), `Altair` (Visualização), `Streamlit` (Web App), `YFinance` (Data Source).

## 📊 Estrutura de Conversão (Lógica de Negócio)

O sistema aplica as seguintes constantes de conversão para garantir a precisão dos dados em toneladas:

* **Milho**: 1 Bushel ≈ 25,401 kg.
* **Soja**: 1 Bushel ≈ 27,215 kg.
* **Cálculo**:
$$\text{Preço Ton} = \left(\frac{\text{Cotação CBOT}}{100}\right) \times \text{Câmbio} \times \text{Fator de Conversão}$$

## 👤 Desenvolvedora

**Thaís Oliveira, Ph.D.** Engenheira de Pesca e Doutora em Aquicultura pela UNESP. Coautora de softwares de nutrição animal registrados no INPI.