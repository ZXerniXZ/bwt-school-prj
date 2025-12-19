import socket
import pickle
import time

HOST = "127.0.0.1"
PORT = 65432

def bwt(s):
    s = s + "$"
    n = len(s)
    rotazioni = [s[i:] + s[:i] for i in range(n)]
    rotazioni.sort()
    return "".join(r[-1] for r in rotazioni)

def handle_client(conn, addr):
    with conn:
        data = conn.recv(4096)
        if not data:
            print(f"Connessione interrotta per: {addr}")
            return

        text = data.decode()
        print(f"Messaggio ricevuto da {addr}: {text}")

        start = time.perf_counter()
        result = bwt(text)
        end = time.perf_counter()

        # Risposta al client: risultato BWT e tempo
        response = (result, end - start)
        conn.sendall(pickle.dumps(response))

print(f"Server in ascolto su {HOST}:{PORT}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        handle_client(conn, addr)
