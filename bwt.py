import socket
import pickle

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connesso al server {HOST}:{PORT}")

    # Invia messaggio
    message = "banana"
    s.send(message.encode())

    # Ricevi e deserializza la tupla
    data = s.recv(1024)
    tupla = pickle.loads(data)  # Converti da bytes a tupla
    print(f"bwt of {message}: {tupla}")   
