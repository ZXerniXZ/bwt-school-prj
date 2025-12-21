#!/usr/bin/env python3
"""
Test di Concorrenza - Verifica thread-safety del file output.json
"""
import socket
import pickle
import threading
import time
import json
import os

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432
NUM_REQUESTS = 20

def send_bwt_request(text, request_id):
    """Invia una richiesta BWT e restituisce l'ID"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((SOCKET_HOST, SOCKET_PORT))
            s.send(text.encode())
            
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                try:
                    result, elapsed = pickle.loads(data)
                    return request_id, True
                except (pickle.UnpicklingError, EOFError):
                    continue
        return request_id, False
    except Exception as e:
        print(f"Errore richiesta {request_id}: {e}")
        return request_id, False

def run_concurrency_test():
    """Esegue test di concorrenza"""
    print("=" * 60)
    print("TEST DI CONCORRENZA - Thread Safety")
    print("=" * 60)
    
    # Leggi il numero attuale di record nel file
    data_file = "/data/output.json"
    if not os.path.exists(data_file):
        data_file = "./data/output.json"
    
    initial_count = 0
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                initial_data = json.load(f)
                initial_count = len(initial_data)
        except:
            pass
    
    print(f"Record iniziali nel file: {initial_count}")
    print(f"Invio {NUM_REQUESTS} richieste simultanee...")
    
    # Prepara le richieste
    threads = []
    results = []
    start_time = time.perf_counter()
    
    # Crea e avvia tutti i thread simultaneamente
    for i in range(NUM_REQUESTS):
        text = f"test_concurrency_{i}"
        t = threading.Thread(target=lambda tid=i, t=text: results.append(send_bwt_request(t, tid)))
        threads.append(t)
    
    # Avvia tutti i thread
    for t in threads:
        t.start()
    
    # Attendi completamento
    for t in threads:
        t.join()
    
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    print(f"Tempo totale: {elapsed:.3f} secondi")
    print(f"Richieste completate: {len([r for r in results if r[1]])}/{NUM_REQUESTS}")
    
    # Attendi un momento per assicurarsi che tutte le scritture siano complete
    time.sleep(2)
    
    # Verifica il file finale
    final_count = 0
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                final_data = json.load(f)
                final_count = len(final_data)
        except Exception as e:
            print(f"Errore lettura file: {e}")
            return None
    
    records_added = final_count - initial_count
    expected_records = NUM_REQUESTS
    
    print(f"\nRecord finali nel file: {final_count}")
    print(f"Record aggiunti: {records_added}")
    print(f"Record attesi: {expected_records}")
    
    if records_added == expected_records:
        print("✅ SUCCESSO: Tutti i record sono stati salvati correttamente!")
        print("   Il lock funziona correttamente, nessuna race condition.")
    else:
        print(f"❌ ERRORE: Mancano {expected_records - records_added} record!")
        print("   Possibile race condition o errore nel salvataggio.")
    
    return {
        'initial_count': initial_count,
        'final_count': final_count,
        'records_added': records_added,
        'expected_records': expected_records,
        'success': records_added == expected_records,
        'elapsed_time': elapsed
    }

if __name__ == '__main__':
    result = run_concurrency_test()
    
    if result:
        import json
        with open('test_results_concurrency.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\nRisultati salvati in test_results_concurrency.json")

