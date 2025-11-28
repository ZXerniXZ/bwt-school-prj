import socket

HOST = "127.0.0.1"      # indirizzo del server
PORT = 65432            # porta del server
message = "banana"      # porta locale fissa del client

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:


    # Connessione al server
    s.connect((HOST, PORT))
    print(f"Connesso al server {HOST}:{PORT}")

    s.send(message.encode())
    data = s.recv(1024)
    print(f"bwt of {message}: {data}")
