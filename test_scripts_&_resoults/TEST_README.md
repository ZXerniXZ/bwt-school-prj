# Guida Esecuzione Test Sistema BWT

## Prerequisiti

1. **Server Socket attivo** sulla porta 65432
   - Docker: `sudo docker-compose up -d`
   - Locale: `python3 server.py`

2. **Server Flask attivo** sulla porta 5050 (opzionale, solo per test overhead)
   - `python3 client.py`

3. **Dipendenze Python**:
   - `requests` (per test overhead): `pip3 install requests`

## Esecuzione Test

### Metodo 1: Esecuzione Automatica (Consigliato)

```bash
python3 run_all_tests.py
```

Questo script:
- Verifica che il server sia attivo
- Esegue tutti i test in sequenza
- Genera il report finale `TEST_REPORT.txt`

### Metodo 2: Esecuzione Manuale

#### 1. Test di Scalabilità
```bash
python3 test_scalability.py
```
Misura i tempi di esecuzione per stringhe di lunghezza crescente.

#### 2. Test di Concorrenza
```bash
python3 test_concurrency.py
```
Verifica che il lock funzioni correttamente con richieste simultanee.

#### 3. Test Casi Edge
```bash
python3 test_edge_cases.py
```
Testa robustezza con caratteri speciali, stringhe vuote, non-ASCII.

#### 4. Test Persistenza
```bash
# Fase 1: Aggiungi dati
python3 test_persistence.py

# Fase 2: Riavvia container e verifica
sudo docker-compose down
sudo docker-compose up -d
sleep 5
python3 test_persistence.py --verify
```

#### 5. Test Overhead (richiede Flask)
```bash
python3 test_overhead.py
```
Confronta latenza Socket diretto vs HTTP Flask.

### Generazione Report

Dopo aver eseguito tutti i test:

```bash
python3 generate_report.py
```

Genera `TEST_REPORT.txt` con tutti i risultati.

## Struttura File di Test

- `test_scalability.py` - Test prestazioni
- `test_concurrency.py` - Test thread-safety
- `test_edge_cases.py` - Test robustezza
- `test_persistence.py` - Test persistenza Docker
- `test_overhead.py` - Test overhead bridge
- `generate_report.py` - Generatore report
- `run_all_tests.py` - Script master

## File di Output

- `test_results_scalability.json` - Risultati scalabilità
- `test_results_concurrency.json` - Risultati concorrenza
- `test_results_edge_cases.json` - Risultati casi edge
- `test_results_persistence.json` - Risultati persistenza
- `test_results_overhead.json` - Risultati overhead
- `TEST_REPORT.txt` - **Report finale completo**

## Note Importanti

1. **Server attivo**: Tutti i test richiedono il server socket attivo
2. **Test persistenza**: Richiede riavvio manuale del container
3. **Test overhead**: Richiede Flask attivo
4. **Tempi**: Alcuni test possono richiedere diversi minuti

## Troubleshooting

### Server non raggiungibile
```bash
# Verifica che il server sia in esecuzione
netstat -tuln | grep 65432

# Se in Docker, verifica container
sudo docker ps | grep bwt-server
```

### Errori di connessione
- Verifica firewall
- Verifica che la porta 65432 sia libera
- Controlla i log del server

### Test falliscono
- Verifica che il server sia completamente avviato
- Controlla i log per errori
- Assicurati che il file `data/output.json` sia accessibile

