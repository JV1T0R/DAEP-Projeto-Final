# Analise de Custos de Producao

Projeto de analise exploratoria dos custos de producao de uma fabrica industrial, com foco em tres componentes de custo: **material**, **mao de obra** e **energia**. O resultado e um relatorio estatistico interativo e um dashboard com 7 visualizacoes geradas diretamente no notebook.

## Dataset

**Arquivo:** `Data/manufacturing_dataset.csv`  
**Fonte:** [Kaggle/Manufacturing Dataset](https://www.kaggle.com/datasets/shreshthvashisht/manufacturing-dataset/data)  
**Registros:** 3.000 entradas de producao diaria  
**Periodo:** Janeiro 2020 a Marco 2028

> O arquivo CSV não está incluído no repositório. Baixe-o pelo link acima e salve em `Data/manufacturing_dataset.csv` antes de executar o notebook.

### Colunas principais utilizadas na analise de custos

| Coluna | Descricao |
|---|---|
| `Date` | Data do registro de producao |
| `Product Type` | Tipo de produto (Appliances, Automotive, Electronics, Furniture, Textiles) |
| `Machine ID` | Identificador da maquina (1–20) |
| `Shift` | Turno de trabalho (Day, Night, Swing) |
| `Units Produced` | Quantidade de unidades produzidas no registro |
| `Production Time Hours` | Horas de producao efetiva |
| `Material Cost Per Unit` | Custo de material por unidade produzida (USD) |
| `Labour Cost Per Hour` | Custo de mao de obra por hora trabalhada (USD) |
| `Energy Consumption kWh` | Consumo de energia no registro (kWh) |

## Estrutura de Arquivos

```
DAEP Projeto Final/
├── Data/
│   └── manufacturing_dataset.csv     # Dataset bruto
├── reports/                          # Figuras geradas pelo notebook
│   ├── fig1_composicao_global.png
│   ├── fig2_por_produto.png
│   ├── fig3_tendencias_temporais.png
│   ├── fig4_por_turno.png
│   ├── fig5_energia.png
│   ├── fig6_por_maquina.png
│   └── fig7_correlacoes.png
├── venv/                             # Ambiente virtual Python
├── cost_analysis.ipynb               # Notebook principal de analise
├── generate_notebook.py              # Script que gera o cost_analysis.ipynb
├── validate_analysis.py              # Script de validacao e geracao das figuras
└── README.md                         # Este arquivo
```

## Como Executar

### Pre-requisitos

Instalar as dependencias no ambiente virtual do projeto:

```bash
venv\Scripts\pip install pandas numpy matplotlib seaborn ipykernel
```

### Opcao 1 — Jupyter Notebook (recomendado)

1. Instalar o Jupyter (se necessario):
   ```bash
   venv\Scripts\pip install notebook
   ```
2. Iniciar o servidor:
   ```bash
   venv\Scripts\jupyter notebook
   ```
3. Abrir `cost_analysis.ipynb` e executar todas as celulas (`Cell > Run All`).

### Opcao 2 — Script direto

Gera todas as figuras em `reports/` sem necessidade do Jupyter:

```bash
venv\Scripts\python validate_analysis.py
```

### Regenerar o notebook

Caso o arquivo `cost_analysis.ipynb` seja alterado e precise ser recriado a partir do codigo-fonte:

```bash
venv\Scripts\python generate_notebook.py
```

## Estrutura do Notebook (`cost_analysis.ipynb`)

### Secao 1 — Configuracao e Carregamento dos Dados
Importa as bibliotecas, define a paleta de cores e os parametros globais (taxa de energia: `$0.12/kWh`). Carrega o CSV, converte datas e verifica valores nulos nas colunas de custo.

### Secao 2 — Calculo das Metricas de Custo
Calcula as colunas derivadas utilizadas em toda a analise:

| Coluna calculada | Formula |
|---|---|
| `Total_Material_Cost` | `Material Cost Per Unit × Units Produced` |
| `Total_Labour_Cost` | `Labour Cost Per Hour × Production Time Hours` |
| `Energy_Cost` | `Energy Consumption kWh × 0.12` |
| `Total_Cost` | Soma dos tres componentes |
| `Cost_Per_Unit` | `Total_Cost / Units Produced` |
| `Material_Pct`, `Labour_Pct`, `Energy_Pct` | Participacao percentual de cada componente |

### Secao 3 — Relatorio Estatistico
Imprime um relatorio textual com:
- Composicao percentual global dos custos
- Breakdown detalhado por tipo de produto (totais, medias, unidades)
- Comparativo por turno
- Estatisticas descritivas do custo por unidade (min, P25, mediana, media, P75, max, desvio padrao)

### Secao 4 — Dashboard de Visualizacoes

| Figura | Conteudo |
|---|---|
| **4.1** Composicao Global | Pie dos 3 componentes · Bar empilhada por produto · Histograma do custo total · Custo medio/unidade por produto |
| **4.2** Por Tipo de Produto | Bar agrupada dos componentes · Boxplot do custo/unidade · Scatter Material×MO · Composicao % horizontal |
| **4.3** Tendencias Temporais | Evolucao mensal do custo total com media movel · Area empilhada dos componentes por mes |
| **4.4** Por Turno | Componentes medios por turno · Boxplot custo/unidade · Custo total acumulado |
| **4.5** Energia | Consumo medio por produto · kWh/unidade · Scatter unidades×energia · Heatmap Produto×Turno |
| **4.6** Por Maquina | Ranking das 20 maquinas por custo/unidade · Heatmap Maquina×Turno |
| **4.7** Correlacoes | Heatmap triangular de Pearson com 12 variaveis de custo e producao |

### Secao 5 — Principais Insights
Calcula e exibe automaticamente os extremos de custo por produto, turno e maquina, alem de recomendacoes de reducao de custos baseadas nos dados.

## Tecnologias

| Biblioteca | Versao | Uso |
|---|---|---|
| pandas | 3.0+ | Manipulacao e agregacao dos dados |
| numpy | 2.4+ | Calculos numericos e arrays |
| matplotlib | 3.10+ | Criacao de todos os graficos |
| seaborn | 0.13+ | Heatmaps e estilizacao |
| ipykernel | 7.3+ | Execucao do notebook no Jupyter |