"""
Script gerador do notebook cost_analysis.ipynb.
Execucao: python generate_notebook.py
"""
import json

_id_n = [0]

def _uid():
    _id_n[0] += 1
    n = _id_n[0]
    return f"c{n:04d}{(n * 2654435761) % (16**8):08x}"[:12]

def code_cell(src):
    return {"cell_type": "code", "id": _uid(), "metadata": {},
            "source": src.strip(), "outputs": [], "execution_count": None}

def md_cell(src):
    return {"cell_type": "markdown", "id": _uid(), "metadata": {}, "source": src.strip()}


TITLE = md_cell("""
# Analise de Custos de Producao

**Dataset:** `Data/manufacturing_dataset.csv` — 3.000 registros de producao industrial
**Objetivo:** Avaliar e visualizar os custos de **material**, **mao de obra** e **energia**

---

## Estrutura do Notebook

| Secao | Descricao |
|---|---|
| 1 | Configuracao e Carregamento dos Dados |
| 2 | Calculo das Metricas de Custo |
| 3 | Relatorio Estatistico |
| 4.1 | Dashboard — Composicao Global |
| 4.2 | Dashboard — Por Tipo de Produto |
| 4.3 | Dashboard — Tendencias Temporais |
| 4.4 | Dashboard — Analise por Turno |
| 4.5 | Dashboard — Analise de Energia |
| 4.6 | Dashboard — Eficiencia por Maquina |
| 4.7 | Dashboard — Mapa de Correlacoes |
| 5 | Principais Insights |
""")

SETUP = code_cell("""
%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.gridspec import GridSpec
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('reports', exist_ok=True)

plt.rcParams.update({
    'figure.dpi': 120,
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'figure.facecolor': 'white',
    'axes.spines.top': False,
    'axes.spines.right': False,
})
sns.set_theme(style='whitegrid', palette='deep')

ENERGY_RATE = 0.12          # USD por kWh (tarifa industrial de referencia)

C_MATERIAL = '#1565C0'
C_LABOUR   = '#C62828'
C_ENERGY   = '#2E7D32'
COST_COLORS = [C_MATERIAL, C_LABOUR, C_ENERGY]
COST_LABELS = ['Material', 'Mao de Obra', 'Energia']

PRODUCT_PALETTE = ['#5C6BC0', '#EF5350', '#26A69A', '#FFA726', '#AB47BC']
SHIFT_PALETTE   = {'Day': '#F9A825', 'Night': '#1565C0', 'Swing': '#2E7D32'}

print("Bibliotecas e configuracoes carregadas com sucesso.")
""")

SEC1_MD = md_cell("## 1. Carregamento e Exploracao dos Dados")

LOAD = code_cell("""
df = pd.read_csv('Data/manufacturing_dataset.csv')

# 'Date' e a coluna de data correta; 'Production ID' contem seriais Excel mal convertidos
df['Date']      = pd.to_datetime(df['Date'])
df['Year']      = df['Date'].dt.year
df['Month']     = df['Date'].dt.month
df['YearMonth'] = df['Date'].dt.to_period('M')

print(f"Registros : {df.shape[0]:,}")
print(f"Colunas   : {df.shape[1]}")
print(f"Periodo   : {df['Date'].min().date()} a {df['Date'].max().date()}")
print(f"Produtos  : {sorted(df['Product Type'].unique())}")
print(f"Turnos    : {sorted(df['Shift'].unique())}")
print(f"Maquinas  : {df['Machine ID'].nunique()} (IDs {df['Machine ID'].min()}–{df['Machine ID'].max()})")

cost_cols = ['Material Cost Per Unit', 'Labour Cost Per Hour',
             'Energy Consumption kWh', 'Units Produced', 'Production Time Hours']
print("\\nValores nulos nas colunas de custo:")
print(df[cost_cols].isnull().sum().to_string())

print("\\nEstatisticas basicas das colunas de custo:")
df[cost_cols].describe().round(2)
""")

SEC2_MD = md_cell("""## 2. Calculo das Metricas de Custo

As metricas derivadas sao calculadas conforme as formulas abaixo:

| Metrica | Formula |
|---|---|
| Custo de Material | `Material Cost Per Unit × Units Produced` |
| Custo de Mao de Obra | `Labour Cost Per Hour × Production Time Hours` |
| Custo de Energia | `Energy Consumption kWh × $0.12/kWh` |
| Custo Total | Soma dos tres componentes |
| Custo por Unidade | `Custo Total / Units Produced` |
""")

COST_CALC = code_cell("""
df['Total_Material_Cost'] = df['Material Cost Per Unit'] * df['Units Produced']
df['Total_Labour_Cost']   = df['Labour Cost Per Hour'] * df['Production Time Hours']
df['Energy_Cost']         = df['Energy Consumption kWh'] * ENERGY_RATE
df['Total_Cost']          = df['Total_Material_Cost'] + df['Total_Labour_Cost'] + df['Energy_Cost']
df['Cost_Per_Unit']       = df['Total_Cost'] / df['Units Produced']

df['Material_Pct'] = df['Total_Material_Cost'] / df['Total_Cost'] * 100
df['Labour_Pct']   = df['Total_Labour_Cost']   / df['Total_Cost'] * 100
df['Energy_Pct']   = df['Energy_Cost']          / df['Total_Cost'] * 100

print("Metricas de custo calculadas com sucesso.\\n")
print("Resumo das novas colunas:")
df[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost',
    'Total_Cost', 'Cost_Per_Unit']].describe().round(2)
""")

SEC3_MD = md_cell("## 3. Relatorio Estatistico")

REPORT = code_cell("""
grand = df['Total_Cost'].sum()
mat   = df['Total_Material_Cost'].sum()
lab   = df['Total_Labour_Cost'].sum()
ene   = df['Energy_Cost'].sum()

sep = '=' * 68

print(sep)
print('  RELATORIO DE CUSTOS DE PRODUCAO')
print(sep)

print('\\n  COMPOSICAO GLOBAL DOS CUSTOS:')
print(f'    Custo de Material   : ${mat:>14,.2f}  ({mat/grand*100:.1f}%)')
print(f'    Custo de Mao de Obra: ${lab:>14,.2f}  ({lab/grand*100:.1f}%)')
print(f'    Custo de Energia    : ${ene:>14,.2f}  ({ene/grand*100:.1f}%)')
print(f'    {chr(8213)*52}')
print(f'    CUSTO TOTAL         : ${grand:>14,.2f}')

print(f'\\n  POR TIPO DE PRODUTO:')
bp = df.groupby('Product Type').agg(
    Custo_Total    = ('Total_Cost',          'sum'),
    Custo_Material = ('Total_Material_Cost', 'sum'),
    Custo_MO       = ('Total_Labour_Cost',   'sum'),
    Custo_Energia  = ('Energy_Cost',         'sum'),
    CPU_Medio      = ('Cost_Per_Unit',       'mean'),
    Unidades       = ('Units Produced',      'sum'),
    Registros      = ('Total_Cost',          'count'),
).sort_values('Custo_Total', ascending=False)

for produto, row in bp.iterrows():
    print(f'\\n  [{produto}]')
    print(f'    Total          : ${row.Custo_Total:>12,.2f}  ({row.Custo_Total/grand*100:.1f}% do total)')
    print(f'    Material       : ${row.Custo_Material:>12,.2f}  ({row.Custo_Material/row.Custo_Total*100:.1f}%)')
    print(f'    Mao de Obra    : ${row.Custo_MO:>12,.2f}  ({row.Custo_MO/row.Custo_Total*100:.1f}%)')
    print(f'    Energia        : ${row.Custo_Energia:>12,.2f}  ({row.Custo_Energia/row.Custo_Total*100:.1f}%)')
    print(f'    Custo/Unidade  : ${row.CPU_Medio:>12,.2f}')
    print(f'    Unidades totais: {row.Unidades:>12,.0f}')
    print(f'    Registros      : {row.Registros:>12,}')

print(f'\\n  POR TURNO:')
bs = df.groupby('Shift').agg(
    Custo_Total  = ('Total_Cost',    'sum'),
    Custo_Medio  = ('Total_Cost',    'mean'),
    CPU_Medio    = ('Cost_Per_Unit', 'mean'),
    Registros    = ('Total_Cost',    'count'),
).sort_values('CPU_Medio')

for turno, row in bs.iterrows():
    print(f'    {turno:<8}: Total=${row.Custo_Total:>13,.2f} | Medio/Run=${row.Custo_Medio:>9,.2f}'
          f' | CPU=${row.CPU_Medio:>7,.2f} | n={row.Registros:,}')

print(f'\\n  CUSTO POR UNIDADE — ESTATISTICAS GLOBAIS:')
s = df['Cost_Per_Unit'].describe()
print(f'    Minimo  : ${s["min"]:>8.2f}')
print(f'    P25     : ${s["25%"]:>8.2f}')
print(f'    Mediana : ${s["50%"]:>8.2f}')
print(f'    Media   : ${s["mean"]:>8.2f}')
print(f'    P75     : ${s["75%"]:>8.2f}')
print(f'    Maximo  : ${s["max"]:>8.2f}')
print(f'    Desvio  : ${s["std"]:>8.2f}')

print(f'\\n{sep}')
""")

SEC4_MD = md_cell("## 4. Dashboard de Visualizacoes")

# ── Figura 1: Composicao Global ──────────────────────────────────────────────
FIG1_MD = md_cell("### 4.1 Composicao Global dos Custos")

FIG1 = code_cell("""
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Composicao Global dos Custos de Producao', fontsize=15, fontweight='bold')

ax = axes[0, 0]
totais = [df['Total_Material_Cost'].sum(), df['Total_Labour_Cost'].sum(), df['Energy_Cost'].sum()]
wedges, texts, autotexts = ax.pie(
    totais, labels=COST_LABELS, colors=COST_COLORS,
    autopct='%1.1f%%', startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    textprops={'fontsize': 11}
)
for at in autotexts:
    at.set_fontsize(11)
    at.set_fontweight('bold')
    at.set_color('white')
ax.set_title('Proporcao dos Componentes de Custo (Total Global)')

ax = axes[0, 1]
bp = df.groupby('Product Type')[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost']].sum() / 1e6
bp.columns = COST_LABELS
bp_sorted = bp.sort_values('Material', ascending=False)
bp_sorted.plot(kind='bar', stacked=True, ax=ax, color=COST_COLORS, edgecolor='white', linewidth=0.5)
ax.set_title('Custo Total por Tipo de Produto (Empilhado)')
ax.set_xlabel('')
ax.set_ylabel('Custo Total (USD Milhoes)')
ax.tick_params(axis='x', rotation=25)
ax.legend(loc='upper right', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))

ax = axes[1, 0]
ax.hist(df['Total_Cost'], bins=60, color='#5C6BC0', edgecolor='white', linewidth=0.4, alpha=0.85)
ax.axvline(df['Total_Cost'].mean(),   color='red',    ls='--', lw=1.8,
           label=f"Media: ${df['Total_Cost'].mean():,.0f}")
ax.axvline(df['Total_Cost'].median(), color='orange', ls='--', lw=1.8,
           label=f"Mediana: ${df['Total_Cost'].median():,.0f}")
ax.set_title('Distribuicao do Custo Total por Registro')
ax.set_xlabel('Custo Total (USD)')
ax.set_ylabel('Frequencia')
ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[1, 1]
cpu_prod = df.groupby('Product Type')['Cost_Per_Unit'].mean().sort_values(ascending=False)
bars = ax.bar(cpu_prod.index, cpu_prod.values,
              color=PRODUCT_PALETTE[:len(cpu_prod)], edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, cpu_prod.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            f'${val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Custo Medio por Unidade Produzida')
ax.set_xlabel('')
ax.set_ylabel('Custo por Unidade (USD)')
ax.tick_params(axis='x', rotation=25)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

plt.tight_layout()
plt.savefig('reports/fig1_composicao_global.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig1_composicao_global.png")
""")

# ── Figura 2: Por Tipo de Produto ───────────────────────────────────────────
FIG2_MD = md_cell("### 4.2 Analise por Tipo de Produto")

FIG2 = code_cell("""
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Analise de Custos por Tipo de Produto', fontsize=15, fontweight='bold')

products = sorted(df['Product Type'].unique())

ax = axes[0, 0]
bp_avg = df.groupby('Product Type')[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost']].mean()
bp_avg.columns = COST_LABELS
bp_avg_sorted = bp_avg.sort_values('Material', ascending=False)
x = np.arange(len(bp_avg_sorted))
w = 0.26
ax.bar(x - w,   bp_avg_sorted['Material'],     w, label='Material',     color=C_MATERIAL, edgecolor='white')
ax.bar(x,       bp_avg_sorted['Mao de Obra'],  w, label='Mao de Obra',  color=C_LABOUR,   edgecolor='white')
ax.bar(x + w,   bp_avg_sorted['Energia'],      w, label='Energia',      color=C_ENERGY,   edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(bp_avg_sorted.index, rotation=25, ha='right')
ax.set_title('Custo Medio dos Componentes por Produto')
ax.set_ylabel('Custo Medio (USD)')
ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[0, 1]
data_by_prod = [df[df['Product Type'] == p]['Cost_Per_Unit'].dropna().values for p in products]
bp_box = ax.boxplot(data_by_prod, patch_artist=True, labels=products,
                    medianprops={'color': 'white', 'linewidth': 2})
for patch, color in zip(bp_box['boxes'], PRODUCT_PALETTE[:len(products)]):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
ax.set_title('Distribuicao do Custo por Unidade (por Produto)')
ax.set_ylabel('Custo por Unidade (USD)')
ax.tick_params(axis='x', rotation=25)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

ax = axes[1, 0]
sample = df.sample(min(500, len(df)), random_state=42)
for prod, color in zip(products, PRODUCT_PALETTE[:len(products)]):
    mask = sample['Product Type'] == prod
    ax.scatter(sample.loc[mask, 'Total_Material_Cost'],
               sample.loc[mask, 'Total_Labour_Cost'],
               alpha=0.55, s=25, color=color, label=prod, edgecolors='none')
ax.set_title('Material vs Mao de Obra por Registro (amostra 500)')
ax.set_xlabel('Custo de Material (USD)')
ax.set_ylabel('Custo de Mao de Obra (USD)')
ax.legend(fontsize=8, loc='upper left')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[1, 1]
pct_avg = df.groupby('Product Type')[['Material_Pct', 'Labour_Pct', 'Energy_Pct']].mean()
pct_avg.columns = COST_LABELS
pct_sorted = pct_avg.sort_values('Material', ascending=True)
y = np.arange(len(pct_sorted))
ax.barh(y, pct_sorted['Material'],     height=0.5, left=0,
        color=C_MATERIAL, label='Material')
ax.barh(y, pct_sorted['Mao de Obra'],  height=0.5,
        left=pct_sorted['Material'],
        color=C_LABOUR, label='Mao de Obra')
ax.barh(y, pct_sorted['Energia'],      height=0.5,
        left=pct_sorted['Material'] + pct_sorted['Mao de Obra'],
        color=C_ENERGY, label='Energia')
ax.set_yticks(y)
ax.set_yticklabels(pct_sorted.index)
ax.set_xlim(0, 100)
ax.set_xlabel('Participacao (%)')
ax.set_title('Composicao Percentual Media do Custo (por Produto)')
ax.legend(loc='lower right', fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))

plt.tight_layout()
plt.savefig('reports/fig2_por_produto.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig2_por_produto.png")
""")

# ── Figura 3: Tendencias Temporais ──────────────────────────────────────────
FIG3_MD = md_cell("### 4.3 Tendencias Temporais dos Custos")

FIG3 = code_cell("""
monthly = df.groupby('YearMonth').agg(
    Mat  = ('Total_Material_Cost', 'sum'),
    Lab  = ('Total_Labour_Cost',   'sum'),
    Ene  = ('Energy_Cost',         'sum'),
    Tot  = ('Total_Cost',          'sum'),
    CPU  = ('Cost_Per_Unit',       'mean'),
).reset_index()
monthly['YearMonth_str'] = monthly['YearMonth'].astype(str)
x_idx = np.arange(len(monthly))

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
fig.suptitle('Tendencias Mensais dos Custos de Producao', fontsize=15, fontweight='bold')

ax = axes[0]
ax.fill_between(x_idx, monthly['Tot'] / 1e3, alpha=0.2, color='#5C6BC0')
ax.plot(x_idx, monthly['Tot'] / 1e3, 'o-', color='#5C6BC0', linewidth=2, markersize=4, label='Custo Total Mensal')
rolling = monthly['Tot'].rolling(window=3, center=True).mean()
ax.plot(x_idx, rolling / 1e3, '--', color='#C62828', linewidth=2, label='Media Movel 3 meses')
tick_step = max(1, len(monthly) // 16)
ax.set_xticks(x_idx[::tick_step])
ax.set_xticklabels(monthly['YearMonth_str'].iloc[::tick_step], rotation=45, ha='right', fontsize=8)
ax.set_title('Custo Total de Producao — Evolucao Mensal')
ax.set_ylabel('Custo (USD mil)')
ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}K'))

ax = axes[1]
ax.stackplot(x_idx,
             monthly['Mat'] / 1e3,
             monthly['Lab'] / 1e3,
             monthly['Ene'] / 1e3,
             labels=COST_LABELS, colors=COST_COLORS, alpha=0.85)
ax.set_xticks(x_idx[::tick_step])
ax.set_xticklabels(monthly['YearMonth_str'].iloc[::tick_step], rotation=45, ha='right', fontsize=8)
ax.set_title('Composicao Mensal dos Custos (Area Empilhada)')
ax.set_ylabel('Custo (USD mil)')
ax.legend(loc='upper left', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}K'))

plt.tight_layout()
plt.savefig('reports/fig3_tendencias_temporais.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig3_tendencias_temporais.png")
""")

# ── Figura 4: Analise por Turno ─────────────────────────────────────────────
FIG4_MD = md_cell("### 4.4 Analise por Turno")

FIG4 = code_cell("""
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle('Analise de Custos por Turno (Day / Night / Swing)', fontsize=15, fontweight='bold')

shifts = ['Day', 'Night', 'Swing']
shift_colors_list = [SHIFT_PALETTE[s] for s in shifts]

ax = axes[0]
shift_avg = df.groupby('Shift')[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost']].mean()
shift_avg = shift_avg.loc[shifts]
shift_avg.columns = COST_LABELS
x = np.arange(len(shifts))
w = 0.26
ax.bar(x - w, shift_avg['Material'],    w, label='Material',    color=C_MATERIAL, edgecolor='white')
ax.bar(x,     shift_avg['Mao de Obra'], w, label='Mao de Obra', color=C_LABOUR,   edgecolor='white')
ax.bar(x + w, shift_avg['Energia'],     w, label='Energia',     color=C_ENERGY,   edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(shifts)
ax.set_title('Custo Medio dos Componentes por Turno')
ax.set_ylabel('Custo Medio (USD)')
ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[1]
data_by_shift = [df[df['Shift'] == s]['Cost_Per_Unit'].dropna().values for s in shifts]
bp = ax.boxplot(data_by_shift, patch_artist=True, labels=shifts,
                medianprops={'color': 'white', 'linewidth': 2})
for patch, color in zip(bp['boxes'], shift_colors_list):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
medians = [np.median(d) for d in data_by_shift]
for i, med in enumerate(medians):
    ax.text(i + 1, med + 0.1, f'${med:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Distribuicao do Custo por Unidade por Turno')
ax.set_ylabel('Custo por Unidade (USD)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

ax = axes[2]
shift_total = df.groupby('Shift')['Total_Cost'].sum() / 1e6
shift_total = shift_total.loc[shifts]
bars = ax.bar(shifts, shift_total.values, color=shift_colors_list, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, shift_total.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'${val:.2f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.set_title('Custo Total Acumulado por Turno')
ax.set_ylabel('Custo Total (USD Milhoes)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))

plt.tight_layout()
plt.savefig('reports/fig4_por_turno.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig4_por_turno.png")
""")

# ── Figura 5: Energia ───────────────────────────────────────────────────────
FIG5_MD = md_cell("### 4.5 Analise de Consumo de Energia")

FIG5 = code_cell("""
df['Energy_Per_Unit'] = df['Energy Consumption kWh'] / df['Units Produced']

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Analise de Consumo e Custo de Energia', fontsize=15, fontweight='bold')

ax = axes[0, 0]
ene_prod = df.groupby('Product Type')['Energy Consumption kWh'].mean().sort_values(ascending=False)
bars = ax.bar(ene_prod.index, ene_prod.values,
              color=PRODUCT_PALETTE[:len(ene_prod)], edgecolor='white')
for bar, val in zip(bars, ene_prod.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{val:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Consumo Medio de Energia por Tipo de Produto')
ax.set_xlabel('')
ax.set_ylabel('Energia Media (kWh/registro)')
ax.tick_params(axis='x', rotation=25)

ax = axes[0, 1]
epu_prod = df.groupby('Product Type')['Energy_Per_Unit'].mean().sort_values(ascending=False)
bars = ax.bar(epu_prod.index, epu_prod.values,
              color=PRODUCT_PALETTE[:len(epu_prod)], edgecolor='white')
for bar, val in zip(bars, epu_prod.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Consumo Medio de Energia por Unidade Produzida')
ax.set_ylabel('kWh / Unidade')
ax.tick_params(axis='x', rotation=25)

ax = axes[1, 0]
sample = df.sample(min(600, len(df)), random_state=7)
for prod, color in zip(sorted(df['Product Type'].unique()), PRODUCT_PALETTE):
    mask = sample['Product Type'] == prod
    ax.scatter(sample.loc[mask, 'Units Produced'],
               sample.loc[mask, 'Energy Consumption kWh'],
               alpha=0.5, s=22, color=color, label=prod, edgecolors='none')
ax.set_title('Unidades Produzidas vs Consumo de Energia (amostra 600)')
ax.set_xlabel('Unidades Produzidas')
ax.set_ylabel('Energia Consumida (kWh)')
ax.legend(fontsize=8)

ax = axes[1, 1]
hm = df.pivot_table(values='Energy Consumption kWh', index='Product Type',
                    columns='Shift', aggfunc='mean')
sns.heatmap(hm, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
            linewidths=0.5, linecolor='white', cbar_kws={'label': 'kWh medio'})
ax.set_title('Consumo Medio de Energia (Produto x Turno)')
ax.set_xlabel('Turno')
ax.set_ylabel('')

plt.tight_layout()
plt.savefig('reports/fig5_energia.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig5_energia.png")
""")

# ── Figura 6: Eficiencia por Maquina ────────────────────────────────────────
FIG6_MD = md_cell("### 4.6 Eficiencia de Custo por Maquina")

FIG6 = code_cell("""
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Analise de Eficiencia de Custo por Maquina', fontsize=15, fontweight='bold')

ax = axes[0]
machine_cpu = df.groupby('Machine ID')['Cost_Per_Unit'].mean().sort_values(ascending=True)
colors_machine = ['#2E7D32' if v <= machine_cpu.median() else '#C62828' for v in machine_cpu.values]
bars = ax.barh(machine_cpu.index.astype(str), machine_cpu.values,
               color=colors_machine, edgecolor='white', linewidth=0.4)
ax.axvline(machine_cpu.mean(), color='navy', ls='--', lw=1.5,
           label=f'Media: ${machine_cpu.mean():.2f}')
for bar, val in zip(bars, machine_cpu.values):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
            f'${val:.2f}', va='center', fontsize=8)
ax.set_title('Custo Medio por Unidade — Ranking das Maquinas')
ax.set_xlabel('Custo Medio por Unidade (USD)')
ax.set_ylabel('Maquina ID')
ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

patch_green = mpatches.Patch(color='#2E7D32', label='Abaixo da mediana (eficiente)')
patch_red   = mpatches.Patch(color='#C62828', label='Acima da mediana (caro)')
ax.legend(handles=[patch_green, patch_red,
                   plt.Line2D([0],[0], color='navy', ls='--', label=f'Media: ${machine_cpu.mean():.2f}')],
          fontsize=8, loc='lower right')

ax = axes[1]
hm_machine = df.pivot_table(values='Cost_Per_Unit', index='Machine ID',
                             columns='Shift', aggfunc='mean')
sns.heatmap(hm_machine, ax=ax, cmap='RdYlGn_r', annot=True, fmt='.1f',
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'Custo/Unidade (USD)'})
ax.set_title('Custo Medio por Unidade — Maquina x Turno')
ax.set_xlabel('Turno')
ax.set_ylabel('Maquina ID')

plt.tight_layout()
plt.savefig('reports/fig6_por_maquina.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig6_por_maquina.png")
""")

# ── Figura 7: Correlacoes ────────────────────────────────────────────────────
FIG7_MD = md_cell("### 4.7 Mapa de Correlacoes")

FIG7 = code_cell("""
cols_corr = [
    'Units Produced', 'Production Time Hours',
    'Material Cost Per Unit', 'Labour Cost Per Hour', 'Energy Consumption kWh',
    'Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost', 'Total_Cost',
    'Cost_Per_Unit', 'Defects', 'Scrap Rate', 'Down time Hours'
]
# Usa colunas que existem no dataframe
cols_available = [c for c in cols_corr if c in df.columns]

# Renomeia para exibicao mais limpa
rename_map = {
    'Units Produced':          'Unidades',
    'Production Time Hours':   'Horas Prod.',
    'Material Cost Per Unit':  'Custo Mat/Un',
    'Labour Cost Per Hour':    'Custo MO/h',
    'Energy Consumption kWh':  'Energia kWh',
    'Total_Material_Cost':     'Total Material',
    'Total_Labour_Cost':       'Total MO',
    'Energy_Cost':             'Total Energia',
    'Total_Cost':              'Custo Total',
    'Cost_Per_Unit':           'Custo/Un',
    'Defects':                 'Defeitos',
    'Scrap Rate':              'Taxa Sucata',
    'Downtime Hours':          'Downtime h',
    'Down time Hours':         'Downtime h',
}
corr_df = df[cols_available].copy()
corr_df.columns = [rename_map.get(c, c) for c in corr_df.columns]

corr_matrix = corr_df.corr(numeric_only=True)

fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, mask=mask, ax=ax,
            cmap='RdBu_r', center=0, vmin=-1, vmax=1,
            annot=True, fmt='.2f', annot_kws={'size': 8},
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'Correlacao de Pearson', 'shrink': 0.8})
ax.set_title('Mapa de Correlacoes — Metricas de Custo e Producao',
             fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('reports/fig7_correlacoes.png', bbox_inches='tight', dpi=150)
plt.show()
print("Figura salva em: reports/fig7_correlacoes.png")
""")

# ── Secao 5: Insights ────────────────────────────────────────────────────────
SEC5_MD = md_cell("## 5. Principais Insights")

INSIGHTS = code_cell("""
grand = df['Total_Cost'].sum()
mat   = df['Total_Material_Cost'].sum()
lab   = df['Total_Labour_Cost'].sum()
ene   = df['Energy_Cost'].sum()

cpu_by_prod  = df.groupby('Product Type')['Cost_Per_Unit'].mean()
prod_mais_caro  = cpu_by_prod.idxmax()
prod_menos_caro = cpu_by_prod.idxmin()

cpu_by_shift = df.groupby('Shift')['Cost_Per_Unit'].mean()
turno_efic   = cpu_by_shift.idxmin()
turno_caro   = cpu_by_shift.idxmax()

cpu_by_mach = df.groupby('Machine ID')['Cost_Per_Unit'].mean()
mach_efic   = cpu_by_mach.idxmin()
mach_cara   = cpu_by_mach.idxmax()

dominante = 'Material' if mat >= lab and mat >= ene else ('Mao de Obra' if lab >= ene else 'Energia')

sep = '=' * 68
print(sep)
print('  PRINCIPAIS INSIGHTS — CUSTOS DE PRODUCAO')
print(sep)

print(f'''
  1. COMPOSICAO DOS CUSTOS
     O componente dominante e "{dominante}", representando {mat/grand*100:.1f}% do custo total.
     - Material   : {mat/grand*100:.1f}% (${mat/1e6:.1f}M)
     - Mao de Obra: {lab/grand*100:.1f}% (${lab/1e6:.1f}M)
     - Energia    : {ene/grand*100:.1f}% (${ene/1e6:.1f}M)

  2. CUSTO POR TIPO DE PRODUTO
     Produto com maior custo por unidade : {prod_mais_caro} (${cpu_by_prod[prod_mais_caro]:.2f}/un)
     Produto com menor custo por unidade : {prod_menos_caro} (${cpu_by_prod[prod_menos_caro]:.2f}/un)
     Diferenca entre extremos: ${cpu_by_prod[prod_mais_caro] - cpu_by_prod[prod_menos_caro]:.2f}/un
     ({(cpu_by_prod[prod_mais_caro] / cpu_by_prod[prod_menos_caro] - 1)*100:.1f}% mais caro)

  3. EFICIENCIA POR TURNO
     Turno mais eficiente (menor CPU): {turno_efic} (${cpu_by_shift[turno_efic]:.2f}/un)
     Turno menos eficiente (maior CPU): {turno_caro}  (${cpu_by_shift[turno_caro]:.2f}/un)

  4. EFICIENCIA POR MAQUINA
     Maquina mais eficiente : ID {mach_efic} (${cpu_by_mach[mach_efic]:.2f}/un)
     Maquina menos eficiente: ID {mach_cara} (${cpu_by_mach[mach_cara]:.2f}/un)

  5. VARIABILIDADE DO CUSTO POR UNIDADE
     CV (Coef. de Variacao) global: {df["Cost_Per_Unit"].std() / df["Cost_Per_Unit"].mean() * 100:.1f}%
     Faixa P5–P95: ${df["Cost_Per_Unit"].quantile(0.05):.2f} a ${df["Cost_Per_Unit"].quantile(0.95):.2f}
''')

print(sep)
print('  RECOMENDACOES')
print(sep)
print(f'''
  - Foco no custo de material: representa a maior parcela ({mat/grand*100:.1f}%).
    Revisar fornecedores e negociar contratos para os produtos de maior volume.

  - Otimizar o turno {turno_caro}: apresenta o maior custo por unidade.
    Investigar causas: horas extras, menor produtividade, manutencao?

  - Benchmark nas maquinas: Maquina {mach_cara} tem custo {(cpu_by_mach[mach_cara]/cpu_by_mach[mach_efic]-1)*100:.0f}%
    acima da Maquina {mach_efic}. Verificar estado de manutencao e operacao.

  - Energia representa {ene/grand*100:.1f}% do custo total — potencial de reducao
    via eficiencia energetica, especialmente nos produtos de maior consumo.
''')
""")

cells = [
    TITLE,
    SETUP,
    SEC1_MD, LOAD,
    SEC2_MD, COST_CALC,
    SEC3_MD, REPORT,
    SEC4_MD,
    FIG1_MD, FIG1,
    FIG2_MD, FIG2,
    FIG3_MD, FIG3,
    FIG4_MD, FIG4,
    FIG5_MD, FIG5,
    FIG6_MD, FIG6,
    FIG7_MD, FIG7,
    SEC5_MD, INSIGHTS,
]

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0",
            "mimetype": "text/x-python",
            "file_extension": ".py"
        }
    },
    "cells": cells
}

out_path = "cost_analysis.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Notebook gerado: {out_path}")
print(f"Total de celulas: {len(cells)}")
