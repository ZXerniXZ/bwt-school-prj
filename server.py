import socket

HOST = "127.0.0.1"
PORT = 65432

def bwt(s):
    s = s + "$"
    n = len(s)

    # Genero tutte le rotazioni usando slicing invece dei doppi cicli
    rotazioni = [s[i:] + s[:i] for i in range(n)]

    rotazioni.sort()

    # Prendo l'ultima colonna
    return "".join(r[-1] for r in rotazioni)

while True:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind( (HOST,PORT) )
        s.listen()

        print(f"server in ascolto su {HOST}:{PORT}")

        conn, addr = s.accept()

        with conn:
            print(f"connessione da {addr}")

            while True:
                data = conn.recv(1024)

                if not data:
                    print(f"connessione interrotta per: {addr}")
                    break

                
                print(f"messaggio ricevuto: {data.decode()}")
                
                stringToSend = bwt(data.decode())

                print(f"messaggio bwt: {stringToSend}")
                
                conn.send(stringToSend.encode())