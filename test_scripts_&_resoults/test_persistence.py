#!/usr/bin/env python3
"""
Test di Persistenza Docker - Verifica che i dati persistano dopo riavvio
"""
import socket
import pickle
import json
import time
import os

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432

def send_bwt(text):
    """Invia richiesta BWT"""
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
                    return True
                except (pickle.UnpicklingError, EOFError):
                    continue
        return False
    except:
        return False

def get_output_via_socket():
    """Ottiene output.json via socket"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((SOCKET_HOST, SOCKET_PORT))
            s.send("GET_OUTPUT".encode())
            
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                try:
                    json_data = json.loads(data.decode())
                    return json_data
                except:
                    continue
            
            # Prova a decodificare come stringa
            try:
                return json.loads(data.decode())
            except:
                return None
    except:
        return None

def run_persistence_test():
    """Esegue test di persistenza"""
    print("=" * 60)
    print("TEST DI PERSISTENZA DOCKER")
    print("=" * 60)
    
    # Fase 1: Stato iniziale
    print("\nFASE 1: Stato iniziale")
    print("-" * 60)
    
    initial_output = get_output_via_socket()
    initial_count = len(initial_output) if initial_output else 0
    print(f"Record iniziali: {initial_count}")
    
    # Fase 2: Aggiungi nuovi record
    print("\nFASE 2: Aggiunta record di test")
    print("-" * 60)
    
    test_strings = [
        f"persistence_test_{i}_{int(time.time())}" 
        for i in range(5)
    ]
    
    print("Invio 5 richieste BWT...")
    for text in test_strings:
        if send_bwt(text):
            print(f"  ✅ '{text}' salvato")
        else:
            print(f"  ❌ Errore salvando '{text}'")
    
    time.sleep(2)  # Attendi scritture
    
    # Fase 3: Verifica record aggiunti
    print("\nFASE 3: Verifica record aggiunti")
    print("-" * 60)
    
    after_output = get_output_via_socket()
    after_count = len(after_output) if after_output else 0
    print(f"Record dopo aggiunta: {after_count}")
    print(f"Record aggiunti: {after_count - initial_count}")
    
    # Verifica che i nostri test record siano presenti
    test_records_found = 0
    if after_output:
        for record in after_output:
            if any(test_str in record.get('stringa_ricevuta', '') for test_str in test_strings):
                test_records_found += 1
    
    print(f"Record di test trovati: {test_records_found}/5")
    
    # Fase 4: Istruzioni per riavvio
    print("\n" + "=" * 60)
    print("FASE 4: ISTRUZIONI PER TEST MANUALE")
    print("=" * 60)
    # Determina il percorso corretto per data/output.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data", "output.json")
    
    print("""
Per completare il test di persistenza:

1. Ferma il container:
   sudo docker-compose down

2. Verifica che il file esista sul host:
   cat """ + data_path + """ | wc -l

3. Riavvia il container:
   sudo docker-compose up -d

4. Attendi che il server sia pronto (circa 5 secondi)

5. Esegui di nuovo questo script per verificare che i dati siano ancora presenti
   cd """ + script_dir + """ && python3 test_persistence.py --verify

I dati dovrebbero essere ancora presenti dopo il riavvio.
""")
    
    return {
        'initial_count': initial_count,
        'after_count': after_count,
        'records_added': after_count - initial_count,
        'test_records_found': test_records_found,
        'test_strings': test_strings
    }

def verify_persistence():
    """Verifica che i dati siano ancora presenti dopo riavvio"""
    print("=" * 60)
    print("VERIFICA PERSISTENZA DOPO RIAVVIO")
    print("=" * 60)
    
    output = get_output_via_socket()
    count = len(output) if output else 0
    
    print(f"\nRecord trovati dopo riavvio: {count}")
    
    if count > 0:
        print("✅ SUCCESSO: I dati sono persistenti!")
        print(f"   Il volume Docker funziona correttamente.")
        
        # Mostra alcuni record
        print("\nUltimi 3 record:")
        for record in output[-3:]:
            print(f"  - {record.get('stringa_ricevuta', 'N/A')}")
    else:
        print("❌ ERRORE: Nessun dato trovato dopo riavvio!")
        print("   Possibile problema con il volume Docker.")
    
    return {
        'count': count,
        'success': count > 0
    }

if __name__ == '__main__':
    import sys
    
    if '--verify' in sys.argv:
        result = verify_persistence()
    else:
        result = run_persistence_test()
    
    # Salva risultati
    with open('test_results_persistence.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\nRisultati salvati in test_results_persistence.json")

