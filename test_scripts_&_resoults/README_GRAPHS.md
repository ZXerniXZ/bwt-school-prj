# Generazione Grafici Prestazione

## Descrizione

Questo script genera due grafici fondamentali per l'analisi delle prestazioni del sistema BWT:

1. **Grafico Scalabilità**: Mostra come il tempo di esecuzione aumenta con la lunghezza della stringa
2. **Grafico Overhead**: Confronta le prestazioni tra Socket diretto e HTTP Flask

## Prerequisiti

```bash
pip install matplotlib numpy
```

Oppure installa tutte le dipendenze:
```bash
pip install -r ../requirements.txt
```

## Esecuzione

```bash
python3 generate_graphs.py
```

## Output

Lo script genera due file PNG ad alta risoluzione (300 DPI):

- `graph_scalability.png` - Grafico scalabilità con curva teorica O(n²log n)
- `graph_overhead_comparison.png` - Confronto overhead Socket vs HTTP

## Dettagli Grafici

### 1. Grafico Scalabilità

- **Asse X**: Lunghezza stringa (scala logaritmica)
- **Asse Y**: Tempo di esecuzione in secondi (scala logaritmica)
- **Linea blu solida**: Tempo di esecuzione reale misurato
- **Linea rosa tratteggiata**: Curva teorica O(n²log n) normalizzata per confronto

Il grafico mostra visivamente come l'implementazione si comporta rispetto alla complessità teorica.

### 2. Grafico Overhead

- **Tipo**: Grafico a barre raggruppate
- **Barre verdi**: Tempo Socket diretto
- **Barre arancioni**: Tempo HTTP Flask
- **Annotazioni gialle**: Percentuale di overhead per ogni categoria

Il grafico evidenzia l'overhead introdotto dal bridge HTTP, mostrando la differenza percentuale per ogni tipo di stringa.

## Note

- I grafici vengono salvati nella stessa directory degli script
- La risoluzione è 300 DPI per una qualità ottimale per documentazione
- I grafici usano scale logaritmiche dove appropriato per migliorare la leggibilità

