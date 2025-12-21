
## Avvio del programma

### Prerequisiti
- Docker e Docker 
- python 3 `pip install -r requirements.txt`

### Avvio tramite Docker
1. Avviare il server: `docker-compose up -d`
   - Il server è disponibile sulla porta 65432
   - I dati vengono salvati nella cartella `./data`

2. Avviare il client web: `python client.py`
   - Il client web è disponibile su http://127.0.0.1:5050

3. Per fermare il server: `docker-compose down`

3. Avviare il client web: `python client.py`
   - Il client web è disponibile su http://127.0.0.1:5050

### Esecuzione test
Per eseguire tutti i test: `python test_scripts_&_resoults/run_all_tests.py`

!disclaimer
tutti gli script di test sono stati generati da IA poichè non direttamente relazionati al funzionamento del sistema ma più verso il test e le automazioni necessarie a quest'ultimo
