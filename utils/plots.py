import pandas as pd
import matplotlib.pyplot as plt
import os

output_dir = '../results/plots'
os.makedirs(output_dir, exist_ok=True)

df_strong = pd.read_csv('../results/dump/dump_data.csv')
df_weak = pd.read_csv('../results/dump/dump_data_weakscaling.csv')
df_chunk = pd.read_csv('../results/dump/dump_data_chunksize.csv')

seq_row = df_strong[df_strong['Implementazione'] == 'Sequenziale'].iloc[0]
t_seq = float(seq_row['Tempo Medio'])
std_seq = float(seq_row['Deviazione Standard'])

df_par = df_strong[df_strong['Implementazione'] == 'Parallela'].copy()
df_par['Threads'] = pd.to_numeric(df_par['Threads'])
df_par['Tempo Medio'] = pd.to_numeric(df_par['Tempo Medio'])
df_par['Deviazione Standard'] = pd.to_numeric(df_par['Deviazione Standard'])

idx_best = df_par.groupby('Threads')['Tempo Medio'].idxmin()
df_best_par = df_par.loc[idx_best].copy()
df_best_par['Speedup'] = t_seq / df_best_par['Tempo Medio']

threads_speedup = [1] + df_best_par['Threads'].tolist()
speedup_values = [1.0] + df_best_par['Speedup'].tolist()

# Grafico 1: Curva di Speedup
plt.figure(figsize=(9, 6))
plt.plot(threads_speedup, speedup_values, marker='o', color='b', linewidth=2, label='Speedup Misurato')
plt.plot([1, 8], [1, 8], 'k--', label='Speedup Ideale (Lineare)')

plt.title('Curva di Speedup (Strong Scaling)', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Threads', fontsize=12)
plt.ylabel('Speedup ($T_{seq} / T_{par}$)', fontsize=12)
plt.xticks(threads_speedup)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.savefig(os.path.join(output_dir, '1_speedup_curve.png'), dpi=300, bbox_inches='tight')
plt.close()

# Grafico 2: Weak Scaling
df_weak['Threads'] = pd.to_numeric(df_weak['Threads'])
t_weak_1 = df_weak[df_weak['Threads'] == 1]['Tempo Medio'].values[0]

x_labels = [f"Th: {row['Threads']}\n(N={int(row['Dataset Size (N)'])})" for _, row in df_weak.iterrows()]

plt.figure(figsize=(9, 6))
plt.plot(df_weak['Threads'], df_weak['Tempo Medio'], marker='s', color='purple', linewidth=2, label='Tempo Misurato')
plt.axhline(y=t_weak_1, color='k', linestyle='--', label='Scalabilità Ideale (Tempo Costante)')

plt.title('Weak Scaling', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Threads e Carico di Lavoro (N)', fontsize=12)
plt.ylabel('Tempo di Esecuzione (Secondi)', fontsize=12)
plt.xticks(df_weak['Threads'], x_labels)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.savefig(os.path.join(output_dir, '2_weak_scaling.png'), dpi=300, bbox_inches='tight')
plt.close()

# Grafico 3: Chunk Size
plt.figure(figsize=(10, 6))

df_chunk['Chunk Size'] = pd.to_numeric(df_chunk['Chunk Size'])
df_chunk['Tempo Medio'] = pd.to_numeric(df_chunk['Tempo Medio'])
df_chunk['Deviazione Standard'] = pd.to_numeric(df_chunk['Deviazione Standard'])
df_chunk = df_chunk.sort_values(by='Chunk Size')

chunk_labels = df_chunk['Chunk Size'].astype(str).tolist()
tempi = df_chunk['Tempo Medio'].tolist()
errori = df_chunk['Deviazione Standard'].tolist()

bars = plt.bar(chunk_labels, tempi, yerr=errori, color='skyblue', edgecolor='black', capsize=5, alpha=0.8)

plt.title('Effetto della Dimensione del Chunk Size (4 Threads)', fontsize=14, fontweight='bold')
plt.xlabel('Dimensione del Chunk Size', fontsize=12)
plt.ylabel('Tempo Medio (Secondi)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, round(yval, 2), ha='center', va='bottom', fontsize=10)

plt.savefig(os.path.join(output_dir, '3_chunk_size_effect.png'), dpi=300, bbox_inches='tight')
plt.close()

# Grafico 4: Tempi di Esecuzione
threads_err = [1] + df_best_par['Threads'].tolist()
times_err = [t_seq] + df_best_par['Tempo Medio'].tolist()
stdev_err = [std_seq] + df_best_par['Deviazione Standard'].tolist()

plt.figure(figsize=(9, 6))
plt.errorbar(threads_err, times_err, yerr=stdev_err, fmt='-o', color='teal',
             ecolor='red', elinewidth=2, capsize=5, capthick=2, markersize=8, label='Wall-clock Time con Std Dev')

plt.title('Wall-clock Time (Migliori Configurazioni)', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Threads', fontsize=12)
plt.ylabel('Tempo di Esecuzione Assoluto (Secondi)', fontsize=12)
plt.xticks(threads_err)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)

for i, (x, y, err) in enumerate(zip(threads_err, times_err, stdev_err)):
    plt.text(x, y + err + 0.5, f"{y:.1f}s\n(±{err:.3f})", ha='center', va='bottom', fontsize=9)

plt.savefig(os.path.join(output_dir, '4_robust_statistics.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"I grafici sono stati generati nella cartella '{output_dir}/'.")