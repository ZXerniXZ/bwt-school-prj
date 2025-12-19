#!/usr/bin/env python3
"""
Genera grafici di prestazione e scalabilità dai risultati dei test
"""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Per generare file senza display

def load_json(filename):
    """Carica file JSON"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_scalability_graph():
    """Genera grafico tempo di esecuzione vs lunghezza stringa"""
    data = load_json('test_results_scalability.json')
    
    if not data or len(data) == 0:
        print("❌ Dati scalabilità non disponibili")
        return False
    
    # Estrai dati
    lengths = [d['length'] for d in data]
    server_times = [d['server_time'] for d in data]
    n2logn_values = [d['n2logn'] for d in data]
    
    # Normalizza n2logn per il grafico (scala per farlo visibile)
    # Trova il fattore di scala per allineare la curva teorica
    max_time = max(server_times)
    max_n2logn = max(n2logn_values)
    scale_factor = max_time / max_n2logn
    
    # Crea grafico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Linea dati reali
    ax.plot(lengths, server_times, 'o-', linewidth=2, markersize=8, 
            label='Tempo di esecuzione reale', color='#2E86AB')
    
    # Linea teorica O(n²log n) normalizzata
    theoretical_times = [n2logn * scale_factor for n2logn in n2logn_values]
    ax.plot(lengths, theoretical_times, '--', linewidth=2, 
            label='Curva teorica O(n²log n) normalizzata', color='#A23B72', alpha=0.7)
    
    # Formattazione
    ax.set_xlabel('Lunghezza Stringa (caratteri)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tempo di Esecuzione (secondi)', fontsize=12, fontweight='bold')
    ax.set_title('Scalabilità BWT: Tempo di Esecuzione vs Lunghezza Stringa', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper left')
    
    # Scala logaritmica per migliorare la visualizzazione
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # Aggiungi annotazioni per i punti (solo per alcuni per non sovraccaricare)
    for i, (length, time) in enumerate(zip(lengths, server_times)):
        if i % 2 == 0 or i == len(lengths) - 1:  # Annota ogni altro punto + ultimo
            ax.annotate(f'{length}', (length, time), 
                       textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
    
    # Salva grafico
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'graph_scalability.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafico scalabilità salvato: graph_scalability.png")
    return True

def generate_overhead_comparison_graph():
    """Genera grafico confronto overhead Socket vs HTTP"""
    data = load_json('test_results_overhead.json')
    
    if not data or len(data) == 0:
        print("❌ Dati overhead non disponibili")
        return False
    
    # Estrai dati
    descriptions = [d['description'] for d in data]
    socket_times = [d['socket']['avg_total'] for d in data]
    flask_times = [d['flask']['avg_total'] for d in data]
    
    # Crea grafico a barre raggruppate
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(descriptions))
    width = 0.35
    
    # Barre
    bars1 = ax.bar(x - width/2, socket_times, width, label='Socket Diretto', 
                   color='#06A77D', alpha=0.8)
    bars2 = ax.bar(x + width/2, flask_times, width, label='HTTP Flask', 
                   color='#F18F01', alpha=0.8)
    
    # Aggiungi valori sulle barre
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}s',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    autolabel(bars1)
    autolabel(bars2)
    
    # Calcola overhead percentuale medio
    overhead_percentages = [d['overhead_percent'] for d in data]
    avg_overhead = sum(overhead_percentages) / len(overhead_percentages)
    
    # Formattazione
    ax.set_xlabel('Tipo di Stringa', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tempo di Risposta (secondi)', fontsize=12, fontweight='bold')
    ax.set_title(f'Confronto Overhead: Socket vs HTTP Flask\n(Overhead medio HTTP: {avg_overhead:.2f}%)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(descriptions, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Aggiungi annotazioni overhead percentuale sopra le barre Flask
    for i, (socket_time, flask_time, overhead_pct) in enumerate(zip(socket_times, flask_times, overhead_percentages)):
        # Annotazione overhead sopra la barra Flask
        ax.text(i + width/2, flask_time, f'+{overhead_pct:.1f}%', 
               ha='center', va='bottom', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFD700', alpha=0.7, edgecolor='black'))
    
    # Salva grafico
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'graph_overhead_comparison.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafico overhead salvato: graph_overhead_comparison.png")
    return True

def main():
    print("=" * 80)
    print("GENERAZIONE GRAFICI PRESTAZIONE E SCALABILITÀ")
    print("=" * 80)
    
    success_count = 0
    
    print("\n1. Generazione grafico scalabilità...")
    if generate_scalability_graph():
        success_count += 1
    
    print("\n2. Generazione grafico confronto overhead...")
    if generate_overhead_comparison_graph():
        success_count += 1
    
    print("\n" + "=" * 80)
    if success_count == 2:
        print("✅ Tutti i grafici generati con successo!")
    else:
        print(f"⚠️  Generati {success_count}/2 grafici")
    print("=" * 80)

if __name__ == '__main__':
    main()

