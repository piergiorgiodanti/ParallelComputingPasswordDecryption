import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

output_dir = '../results/plots'
os.makedirs(output_dir, exist_ok=True)

df_strong = pd.read_csv('../results/dump/dump_data.csv')
df_weak = pd.read_csv('../results/dump/dump_data_weakscaling.csv')
df_chunk = pd.read_csv('../results/dump/dump_data_chunksize.csv')

seq_row = df_strong[df_strong['Implementazione'] == 'Sequenziale'].iloc[0]
t_seq = float(seq_row['Tempo Medio'])
std_seq = float(seq_row['Deviazione Standard'])

df_pool = df_strong[df_strong['Implementazione'] == 'Parallel Pool'].copy()

for df in [df_pool]:
    df['Threads'] = pd.to_numeric(df['Threads'])
    df['Tempo Medio'] = pd.to_numeric(df['Tempo Medio'])
    df['Deviazione Standard'] = pd.to_numeric(df['Deviazione Standard'])
    df.sort_values(by='Threads', inplace=True)

df_pool['Speedup'] = t_seq / df_pool['Tempo Medio']

threads_list = [1] + df_pool['Threads'].tolist()
speedup_pool = [1.0] + df_pool['Speedup'].tolist()

# Grafico 1: Speedup
plt.figure(figsize=(9, 6))
plt.plot(threads_list, speedup_pool, marker='o', color='b', linewidth=2, label='Speedup (Parallel Pool)')
plt.plot([1, max(threads_list)], [1, max(threads_list)], 'k--', label='Speedup Ideale (Lineare)')

plt.title('Curva di Speedup (Strong Scaling)', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Threads', fontsize=12)
plt.ylabel('Speedup (T_seq / T_par)', fontsize=12)
plt.xticks(threads_list)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.savefig(os.path.join(output_dir, '1_speedup_curve.png'), dpi=300, bbox_inches='tight')
plt.close()

# Grafico 2: Weak Scaling
df_weak['Threads'] = pd.to_numeric(df_weak['Threads'])
df_weak_pool = df_weak[df_weak['Implementazione'] == 'Parallel Pool'].sort_values(by='Threads')

t_weak_1 = df_weak_pool[df_weak_pool['Threads'] == 1]['Tempo Medio'].values[0]
x_labels = [f"Th: {row['Threads']}\n(N={int(row['Dataset Size (N)'])})" for _, row in df_weak_pool.iterrows()]

plt.figure(figsize=(9, 6))
plt.plot(df_weak_pool['Threads'], df_weak_pool['Tempo Medio'], marker='s', color='purple', linewidth=2,
         label='Tempo (Parallel Pool)')
plt.axhline(y=t_weak_1, color='k', linestyle='--', label='Scalabilità Ideale (Tempo Costante)')

plt.title('Weak Scaling', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Threads e Carico di Lavoro (N)', fontsize=12)
plt.ylabel('Tempo di Esecuzione (Secondi)', fontsize=12)
plt.xticks(df_weak_pool['Threads'], x_labels)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.savefig(os.path.join(output_dir, '2_weak_scaling.png'), dpi=300, bbox_inches='tight')
plt.close()

# Grafico 3: Chunk Size
plt.figure(figsize=(10, 6))

df_chunk['Chunk Size'] = pd.to_numeric(df_chunk['Chunk Size'])
df_chunk['Tempo Medio'] = pd.to_numeric(df_chunk['Tempo Medio'])
df_chunk['Deviazione Standard'] = pd.to_numeric(df_chunk['Deviazione Standard'])

chunk_sizes = sorted(df_chunk['Chunk Size'].unique(), reverse=True)
x = np.arange(len(chunk_sizes))
width = 0.35

pool_means, pool_stds = [], []
threads_means, threads_stds = [], []

for val in chunk_sizes:
    p_row = df_chunk[(df_chunk['Implementazione'] == 'Parallel Pool') & (df_chunk['Chunk Size'] == val)]

    pool_means.append(p_row['Tempo Medio'].values[0])
    pool_stds.append(p_row['Deviazione Standard'].values[0])

fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar(x - width / 2, pool_means, width, yerr=pool_stds, label='Parallel Pool', color='skyblue',
               edgecolor='black', capsize=5)

ax.set_title('Effetto della Dimensione del Chunk Size (4 Threads)', fontsize=14, fontweight='bold')
ax.set_xlabel('Dimensione del Chunk Size', fontsize=12)
ax.set_ylabel('Tempo Medio (Secondi)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels([str(cs) for cs in chunk_sizes])
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.legend(fontsize=11)


def autolabel(bars):
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.5, round(yval, 2), ha='center', va='bottom', fontsize=9)


autolabel(bars1)

plt.savefig(os.path.join(output_dir, '3_chunk_size_effect.png'), dpi=300, bbox_inches='tight')
plt.close(fig)
plt.close()

# Grafico 4: Tempi di esecuzione
times_pool = [t_seq] + df_pool['Tempo Medio'].tolist()
stdev_pool = [std_seq] + df_pool['Deviazione Standard'].tolist()

plt.figure(figsize=(10, 6))
plt.errorbar(threads_list, times_pool, yerr=stdev_pool, fmt='-o', color='teal',
             ecolor='teal', elinewidth=2, capsize=5, markersize=8, label='Parallel Pool')

plt.title('Wall-clock Time', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Threads', fontsize=12)
plt.ylabel('Tempo di Esecuzione Assoluto (Secondi)', fontsize=12)
plt.xticks(threads_list)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)

plt.savefig(os.path.join(output_dir, '4_robust_statistics.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"I grafici sono stati generati nella cartella '{output_dir}/'.")