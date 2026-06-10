"""Gera todas as figuras de analise de custo em reports/ sem necessidade do Jupyter."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
import os, warnings
warnings.filterwarnings('ignore')

os.makedirs('reports', exist_ok=True)
sns.set_theme(style='whitegrid')
plt.rcParams.update({'figure.dpi': 120, 'font.size': 10,
                     'axes.titlesize': 12, 'axes.titleweight': 'bold',
                     'figure.facecolor': 'white'})

ENERGY_RATE = 0.12
C_MATERIAL = '#1565C0'; C_LABOUR = '#C62828'; C_ENERGY = '#2E7D32'
COST_COLORS = [C_MATERIAL, C_LABOUR, C_ENERGY]
COST_LABELS = ['Material', 'Mao de Obra', 'Energia']
PRODUCT_PALETTE = ['#5C6BC0', '#EF5350', '#26A69A', '#FFA726', '#AB47BC']
SHIFT_PALETTE = {'Day': '#F9A825', 'Night': '#1565C0', 'Swing': '#2E7D32'}

# 'Date' e a coluna de data correta; 'Production ID' contem seriais Excel mal convertidos
df = pd.read_csv('Data/manufacturing_dataset.csv')
df['Date']      = pd.to_datetime(df['Date'])
df['Year']      = df['Date'].dt.year
df['Month']     = df['Date'].dt.month
df['YearMonth'] = df['Date'].dt.to_period('M')

df['Total_Material_Cost'] = df['Material Cost Per Unit'] * df['Units Produced']
df['Total_Labour_Cost']   = df['Labour Cost Per Hour'] * df['Production Time Hours']
df['Energy_Cost']         = df['Energy Consumption kWh'] * ENERGY_RATE
df['Total_Cost']          = df['Total_Material_Cost'] + df['Total_Labour_Cost'] + df['Energy_Cost']
df['Cost_Per_Unit']       = df['Total_Cost'] / df['Units Produced']
df['Material_Pct']        = df['Total_Material_Cost'] / df['Total_Cost'] * 100
df['Labour_Pct']          = df['Total_Labour_Cost']   / df['Total_Cost'] * 100
df['Energy_Pct']          = df['Energy_Cost']          / df['Total_Cost'] * 100
df['Energy_Per_Unit']     = df['Energy Consumption kWh'] / df['Units Produced']

grand = df['Total_Cost'].sum()
mat   = df['Total_Material_Cost'].sum()
lab   = df['Total_Labour_Cost'].sum()
ene   = df['Energy_Cost'].sum()

print(f"Registros : {df.shape[0]:,}")
print(f"Periodo   : {df['Date'].min().date()} a {df['Date'].max().date()}")
print(f"Produtos  : {sorted(df['Product Type'].unique())}")
print(f"CUSTO TOTAL: ${grand:,.2f}")
print(f"  Material  : ${mat:,.2f} ({mat/grand*100:.1f}%)")
print(f"  Mao Obra  : ${lab:,.2f} ({lab/grand*100:.1f}%)")
print(f"  Energia   : ${ene:,.2f} ({ene/grand*100:.1f}%)")
print(f"CPU medio   : ${df['Cost_Per_Unit'].mean():.2f}")
print()

products   = sorted(df['Product Type'].unique())
shifts     = ['Day', 'Night', 'Swing']
shift_cols = [SHIFT_PALETTE[s] for s in shifts]

print("Gerando fig1...")
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Composicao Global dos Custos de Producao', fontsize=15, fontweight='bold')

ax = axes[0, 0]
totais = [mat, lab, ene]
wedges, texts, autotexts = ax.pie(
    totais, labels=COST_LABELS, colors=COST_COLORS, autopct='%1.1f%%',
    startangle=140, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
for at in autotexts:
    at.set_fontsize(11); at.set_fontweight('bold'); at.set_color('white')
ax.set_title('Proporcao dos Componentes de Custo (Total Global)')

ax = axes[0, 1]
bp = df.groupby('Product Type')[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost']].sum() / 1e6
bp.columns = COST_LABELS
bp.sort_values('Material', ascending=False).plot(
    kind='bar', stacked=True, ax=ax, color=COST_COLORS, edgecolor='white', linewidth=0.5)
ax.set_title('Custo Total por Tipo de Produto (Empilhado)')
ax.set_xlabel(''); ax.tick_params(axis='x', rotation=25)
ax.legend(loc='upper right', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))

ax = axes[1, 0]
ax.hist(df['Total_Cost'], bins=60, color='#5C6BC0', edgecolor='white', linewidth=0.4, alpha=0.85)
ax.axvline(df['Total_Cost'].mean(), color='red', ls='--', lw=1.8,
           label=f"Media: ${df['Total_Cost'].mean():,.0f}")
ax.axvline(df['Total_Cost'].median(), color='orange', ls='--', lw=1.8,
           label=f"Mediana: ${df['Total_Cost'].median():,.0f}")
ax.set_title('Distribuicao do Custo Total por Registro')
ax.set_xlabel('Custo Total (USD)'); ax.set_ylabel('Frequencia'); ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[1, 1]
cpu_prod = df.groupby('Product Type')['Cost_Per_Unit'].mean().sort_values(ascending=False)
bars = ax.bar(cpu_prod.index, cpu_prod.values,
              color=PRODUCT_PALETTE[:len(cpu_prod)], edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, cpu_prod.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            f'${val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Custo Medio por Unidade Produzida')
ax.set_xlabel(''); ax.tick_params(axis='x', rotation=25)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

plt.tight_layout()
plt.savefig('reports/fig1_composicao_global.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig1_composicao_global.png")

print("Gerando fig2...")
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Analise de Custos por Tipo de Produto', fontsize=15, fontweight='bold')

bp_avg = df.groupby('Product Type')[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost']].mean()
bp_avg.columns = COST_LABELS
bp_avg_sorted = bp_avg.sort_values('Material', ascending=False)
ax = axes[0, 0]
x = np.arange(len(bp_avg_sorted)); w = 0.26
ax.bar(x - w, bp_avg_sorted['Material'],    w, label='Material',    color=C_MATERIAL, edgecolor='white')
ax.bar(x,     bp_avg_sorted['Mao de Obra'], w, label='Mao de Obra', color=C_LABOUR,   edgecolor='white')
ax.bar(x + w, bp_avg_sorted['Energia'],     w, label='Energia',     color=C_ENERGY,   edgecolor='white')
ax.set_xticks(x); ax.set_xticklabels(bp_avg_sorted.index, rotation=25, ha='right')
ax.set_title('Custo Medio dos Componentes por Produto'); ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[0, 1]
data_by_prod = [df[df['Product Type'] == p]['Cost_Per_Unit'].dropna().values for p in products]
bp_box = ax.boxplot(data_by_prod, patch_artist=True, labels=products,
                    medianprops={'color': 'white', 'linewidth': 2})
for patch, color in zip(bp_box['boxes'], PRODUCT_PALETTE[:len(products)]):
    patch.set_facecolor(color); patch.set_alpha(0.8)
ax.set_title('Distribuicao do Custo por Unidade (por Produto)')
ax.set_ylabel('Custo por Unidade (USD)'); ax.tick_params(axis='x', rotation=25)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

ax = axes[1, 0]
sample = df.sample(500, random_state=42)
for prod, color in zip(products, PRODUCT_PALETTE[:len(products)]):
    mask = sample['Product Type'] == prod
    ax.scatter(sample.loc[mask, 'Total_Material_Cost'], sample.loc[mask, 'Total_Labour_Cost'],
               alpha=0.55, s=25, color=color, label=prod, edgecolors='none')
ax.set_title('Material vs Mao de Obra por Registro (amostra 500)')
ax.set_xlabel('Custo de Material (USD)'); ax.set_ylabel('Custo de Mao de Obra (USD)')
ax.legend(fontsize=8)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[1, 1]
pct_avg = df.groupby('Product Type')[['Material_Pct', 'Labour_Pct', 'Energy_Pct']].mean()
pct_avg.columns = COST_LABELS
pct_sorted = pct_avg.sort_values('Material', ascending=True)
y = np.arange(len(pct_sorted))
ax.barh(y, pct_sorted['Material'],                                         height=0.5, color=C_MATERIAL, label='Material')
ax.barh(y, pct_sorted['Mao de Obra'], left=pct_sorted['Material'],         height=0.5, color=C_LABOUR,   label='Mao de Obra')
ax.barh(y, pct_sorted['Energia'],     left=pct_sorted['Material'] + pct_sorted['Mao de Obra'],
        height=0.5, color=C_ENERGY, label='Energia')
ax.set_yticks(y); ax.set_yticklabels(pct_sorted.index)
ax.set_title('Composicao Percentual Media do Custo (por Produto)'); ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))

plt.tight_layout()
plt.savefig('reports/fig2_por_produto.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig2_por_produto.png")

print("Gerando fig3...")
monthly = df.groupby('YearMonth').agg(
    Mat=('Total_Material_Cost', 'sum'),
    Lab=('Total_Labour_Cost',   'sum'),
    Ene=('Energy_Cost',         'sum'),
    Tot=('Total_Cost',          'sum'),
).reset_index()
monthly['YM_str'] = monthly['YearMonth'].astype(str)
x_idx = np.arange(len(monthly))

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
fig.suptitle('Tendencias Mensais dos Custos de Producao', fontsize=15, fontweight='bold')

ax = axes[0]
ax.fill_between(x_idx, monthly['Tot'] / 1e3, alpha=0.2, color='#5C6BC0')
ax.plot(x_idx, monthly['Tot'] / 1e3, 'o-', color='#5C6BC0', lw=2, ms=4, label='Custo Total Mensal')
rolling = monthly['Tot'].rolling(window=3, center=True).mean()
ax.plot(x_idx, rolling / 1e3, '--', color='#C62828', lw=2, label='Media Movel 3 meses')
step = max(1, len(monthly) // 16)
ax.set_xticks(x_idx[::step])
ax.set_xticklabels(monthly['YM_str'].iloc[::step], rotation=45, ha='right', fontsize=8)
ax.set_title('Custo Total de Producao — Evolucao Mensal')
ax.set_ylabel('Custo (USD mil)'); ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}K'))

ax = axes[1]
ax.stackplot(x_idx,
             monthly['Mat'] / 1e3, monthly['Lab'] / 1e3, monthly['Ene'] / 1e3,
             labels=COST_LABELS, colors=COST_COLORS, alpha=0.85)
ax.set_xticks(x_idx[::step])
ax.set_xticklabels(monthly['YM_str'].iloc[::step], rotation=45, ha='right', fontsize=8)
ax.set_title('Composicao Mensal dos Custos (Area Empilhada)')
ax.set_ylabel('Custo (USD mil)'); ax.legend(loc='upper left', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}K'))

plt.tight_layout()
plt.savefig('reports/fig3_tendencias_temporais.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig3_tendencias_temporais.png")

print("Gerando fig4...")
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle('Analise de Custos por Turno (Day / Night / Swing)', fontsize=15, fontweight='bold')

shift_avg = df.groupby('Shift')[['Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost']].mean()
shift_avg = shift_avg.loc[shifts]; shift_avg.columns = COST_LABELS
ax = axes[0]; x = np.arange(3); w = 0.26
ax.bar(x - w, shift_avg['Material'],    w, label='Material',    color=C_MATERIAL, edgecolor='white')
ax.bar(x,     shift_avg['Mao de Obra'], w, label='Mao de Obra', color=C_LABOUR,   edgecolor='white')
ax.bar(x + w, shift_avg['Energia'],     w, label='Energia',     color=C_ENERGY,   edgecolor='white')
ax.set_xticks(x); ax.set_xticklabels(shifts)
ax.set_title('Custo Medio dos Componentes por Turno'); ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

ax = axes[1]
data_by_shift = [df[df['Shift'] == s]['Cost_Per_Unit'].dropna().values for s in shifts]
bp = ax.boxplot(data_by_shift, patch_artist=True, labels=shifts,
                medianprops={'color': 'white', 'linewidth': 2})
for patch, color in zip(bp['boxes'], shift_cols):
    patch.set_facecolor(color); patch.set_alpha(0.8)
for i, d in enumerate(data_by_shift):
    med = np.median(d)
    ax.text(i + 1, med + 0.1, f'${med:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Distribuicao do Custo por Unidade por Turno')
ax.set_ylabel('Custo por Unidade (USD)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

ax = axes[2]
shift_total = df.groupby('Shift')['Total_Cost'].sum() / 1e6
shift_total = shift_total.loc[shifts]
bars = ax.bar(shifts, shift_total.values, color=shift_cols, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, shift_total.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'${val:.2f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.set_title('Custo Total Acumulado por Turno')
ax.set_ylabel('Custo Total (USD Milhoes)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))

plt.tight_layout()
plt.savefig('reports/fig4_por_turno.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig4_por_turno.png")

print("Gerando fig5...")
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
ax.set_ylabel('Energia Media (kWh)'); ax.tick_params(axis='x', rotation=25)

ax = axes[0, 1]
epu_prod = df.groupby('Product Type')['Energy_Per_Unit'].mean().sort_values(ascending=False)
bars = ax.bar(epu_prod.index, epu_prod.values,
              color=PRODUCT_PALETTE[:len(epu_prod)], edgecolor='white')
for bar, val in zip(bars, epu_prod.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_title('Energia Media por Unidade Produzida')
ax.set_ylabel('kWh / Unidade'); ax.tick_params(axis='x', rotation=25)

ax = axes[1, 0]
sample = df.sample(600, random_state=7)
for prod, color in zip(products, PRODUCT_PALETTE[:len(products)]):
    mask = sample['Product Type'] == prod
    ax.scatter(sample.loc[mask, 'Units Produced'],
               sample.loc[mask, 'Energy Consumption kWh'],
               alpha=0.5, s=22, color=color, label=prod, edgecolors='none')
ax.set_title('Unidades Produzidas vs Consumo de Energia (amostra 600)')
ax.set_xlabel('Unidades Produzidas'); ax.set_ylabel('Energia Consumida (kWh)')
ax.legend(fontsize=8)

ax = axes[1, 1]
hm = df.pivot_table(values='Energy Consumption kWh',
                    index='Product Type', columns='Shift', aggfunc='mean')
sns.heatmap(hm, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
            linewidths=0.5, linecolor='white', cbar_kws={'label': 'kWh medio'})
ax.set_title('Consumo Medio de Energia (Produto x Turno)')
ax.set_xlabel('Turno'); ax.set_ylabel('')

plt.tight_layout()
plt.savefig('reports/fig5_energia.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig5_energia.png")

print("Gerando fig6...")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Analise de Eficiencia de Custo por Maquina', fontsize=15, fontweight='bold')

ax = axes[0]
machine_cpu = df.groupby('Machine ID')['Cost_Per_Unit'].mean().sort_values(ascending=True)
colors_machine = ['#2E7D32' if v <= machine_cpu.median() else '#C62828' for v in machine_cpu.values]
bars = ax.barh(machine_cpu.index.astype(str), machine_cpu.values,
               color=colors_machine, edgecolor='white', linewidth=0.4)
ax.axvline(machine_cpu.mean(), color='navy', ls='--', lw=1.5)
for bar, val in zip(bars, machine_cpu.values):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
            f'${val:.2f}', va='center', fontsize=8)
patch_g = mpatches.Patch(color='#2E7D32', label='Abaixo da mediana (eficiente)')
patch_r = mpatches.Patch(color='#C62828', label='Acima da mediana (caro)')
ax.legend(handles=[patch_g, patch_r,
                   plt.Line2D([0],[0], color='navy', ls='--',
                              label=f'Media: ${machine_cpu.mean():.2f}')],
          fontsize=8, loc='lower right')
ax.set_title('Ranking de Maquinas por Custo Medio por Unidade')
ax.set_xlabel('Custo Medio por Unidade (USD)'); ax.set_ylabel('Maquina ID')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

ax = axes[1]
hm_machine = df.pivot_table(values='Cost_Per_Unit',
                             index='Machine ID', columns='Shift', aggfunc='mean')
sns.heatmap(hm_machine, ax=ax, cmap='RdYlGn_r', annot=True, fmt='.1f',
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'Custo/Unidade (USD)'})
ax.set_title('Custo Medio por Unidade — Maquina x Turno')
ax.set_xlabel('Turno'); ax.set_ylabel('Maquina ID')

plt.tight_layout()
plt.savefig('reports/fig6_por_maquina.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig6_por_maquina.png")

print("Gerando fig7...")
cols_corr = ['Units Produced', 'Production Time Hours', 'Material Cost Per Unit',
             'Labour Cost Per Hour', 'Energy Consumption kWh',
             'Total_Material_Cost', 'Total_Labour_Cost', 'Energy_Cost',
             'Total_Cost', 'Cost_Per_Unit', 'Defects', 'Scrap Rate']
cols_available = [c for c in cols_corr if c in df.columns]
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
}
corr_df = df[cols_available].copy()
corr_df.columns = [rename_map.get(c, c) for c in corr_df.columns]
corr_matrix = corr_df.corr(numeric_only=True)

fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, mask=mask, ax=ax, cmap='RdBu_r',
            center=0, vmin=-1, vmax=1,
            annot=True, fmt='.2f', annot_kws={'size': 8},
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'Correlacao de Pearson', 'shrink': 0.8})
ax.set_title('Mapa de Correlacoes — Metricas de Custo e Producao',
             fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('reports/fig7_correlacoes.png', bbox_inches='tight', dpi=150)
plt.close()
print("  OK -> reports/fig7_correlacoes.png")

print()
cpu_by_prod  = df.groupby('Product Type')['Cost_Per_Unit'].mean()
cpu_by_shift = df.groupby('Shift')['Cost_Per_Unit'].mean()
cpu_by_mach  = df.groupby('Machine ID')['Cost_Per_Unit'].mean()

print("=== INSIGHTS PRINCIPAIS ===")
print(f"Prod. mais caro/un   : {cpu_by_prod.idxmax()} (${cpu_by_prod.max():.2f})")
print(f"Prod. menos caro/un  : {cpu_by_prod.idxmin()} (${cpu_by_prod.min():.2f})")
print(f"Turno mais eficiente : {cpu_by_shift.idxmin()} (${cpu_by_shift.min():.2f}/un)")
print(f"Turno menos eficiente: {cpu_by_shift.idxmax()} (${cpu_by_shift.max():.2f}/un)")
print(f"Maquina mais efic.   : ID {cpu_by_mach.idxmin()} (${cpu_by_mach.min():.2f}/un)")
print(f"Maquina menos efic.  : ID {cpu_by_mach.idxmax()} (${cpu_by_mach.max():.2f}/un)")

import os
files = sorted(os.listdir('reports'))
print(f"\nFiguras geradas ({len(files)}):")
for f in files:
    size = os.path.getsize(f'reports/{f}') // 1024
    print(f"  reports/{f}  ({size} KB)")
