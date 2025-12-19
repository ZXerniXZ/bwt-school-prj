import socket
import pickle
import time
import threading
import json
import os   

HOST = "0.0.0.0"  # Ascolta su tutte le interfacce per permettere connessioni esterne
PORT = 65432
KEYWORD_GET_OUTPUT = "GET_OUTPUT"  # Parola chiave per richiedere output.json

# Lock per sincronizzare l'accesso al file output.json
file_lock = threading.Lock()

def bwt(s):
    s = s + "$"
    n = len(s)
    rotazioni = [s[i:] + s[:i] for i in range(n)]
    rotazioni.sort()
    return "".join(r[-1] for r in rotazioni)


def salva_record(record):
    # Cartella per i dati (mappata come volume esterno)
    data_dir = "/data"
    file_name = os.path.join(data_dir, "output.json")
    
    # Crea la cartella se non esiste
    os.makedirs(data_dir, exist_ok=True)

    # Acquisisci il lock per sincronizzare l'accesso al file
    with file_lock:
        # Se il file esiste lo carico, altrimenti creo lista vuota
        if os.path.exists(file_name) and os.path.isfile(file_name):
            with open(file_name, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []    
        else:
            data = []

        data.append(record)

        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)


def handle_client(conn, addr):
    with conn:
        data = conn.recv(4096)
        if not data:
            print(f"Connessione interrotta per: {addr}")
            return

        text = data.decode()
        print(f"Messaggio ricevuto: {text}")

        # Controlla se il messaggio contiene la parola chiave per ottenere output.json
        if KEYWORD_GET_OUTPUT in text:
            # Endpoint per ottenere output.json
            data_dir = "/data"
            file_name = os.path.join(data_dir, "output.json")
            
            # Acquisisci il lock per sincronizzare la lettura del file
            with file_lock:
                if os.path.exists(file_name) and os.path.isfile(file_name):
                    try:
                        with open(file_name, "r") as f:
                            json_data = json.load(f)
                        # Invia il JSON come stringa
                        response_json = json.dumps(json_data, indent=4)
                        conn.sendall(response_json.encode())
                        print(f"Output.json inviato a {addr}")
                    except Exception as e:
                        error_msg = f"Errore nella lettura del file: {str(e)}"
                        conn.sendall(error_msg.encode())
                        print(error_msg)
                else:
                    error_msg = "File output.json non trovato"
                    conn.sendall(error_msg.encode())
                    print(error_msg)
        else:
            # Logica BWT normale
            start = time.perf_counter()
            result = bwt(text)
            end = time.perf_counter()

            data_to_save = {
                "stringa_ricevuta": text,
                "stringa_bwt": result,
                "tempo_secondi": end - start
            }

            # Salvo sul JSON in modo corretto
            salva_record(data_to_save)

            # Risposta al client (mantengo solo il risultato BWT)
            response = (result,end - start)
            conn.sendall(pickle.dumps(response))


print(f"Server in ascolto su {HOST}:{PORT}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()
