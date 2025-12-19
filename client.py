from flask import Flask, render_template_string, request, jsonify
import socket
import pickle
import json

app = Flask(__name__)

# Configurazione del server socket
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432
KEYWORD_GET_OUTPUT = "GET_OUTPUT"

# HTML template semplice
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BWT Server</title>
</head>
<body>
    <h1>BWT Server</h1>
    
    <h2>Trasforma Stringa con BWT</h2>
    <input type="text" id="bwtInput">
    <button onclick="transformBWT()">Trasforma</button>
    <div id="bwtLoading" style="display:none">Elaborazione in corso...</div>
    <div id="bwtResult"></div>
    
    <h2>Visualizza Output JSON</h2>
    <button onclick="getOutput()">Carica Output.json</button>
    <div id="outputLoading" style="display:none">Caricamento in corso...</div>
    <div id="outputResult"></div>

    <script>
        async function transformBWT() {
            const input = document.getElementById('bwtInput').value.trim();
            const resultDiv = document.getElementById('bwtResult');
            const loadingDiv = document.getElementById('bwtLoading');
            
            if (!input) {
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>Errore: Inserisci una stringa</p>';
                return;
            }
            
            resultDiv.style.display = 'none';
            loadingDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/bwt', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text: input })
                });
                
                const data = await response.json();
                loadingDiv.style.display = 'none';
                
                if (data.success) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<p>Stringa originale: ' + data.original + '</p><p>Risultato BWT: ' + data.result + '</p><p>Tempo: ' + data.elapsed_time.toFixed(6) + ' secondi</p>';
                } else {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<p>Errore: ' + (data.error || 'Errore sconosciuto') + '</p>';
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>Errore: ' + error.message + '</p>';
            }
        }
        
        async function getOutput() {
            const resultDiv = document.getElementById('outputResult');
            const loadingDiv = document.getElementById('outputLoading');
            
            resultDiv.style.display = 'none';
            loadingDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/output');
                const data = await response.json();
                loadingDiv.style.display = 'none';
                
                if (data.success) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<pre>' + JSON.stringify(data.output, null, 2) + '</pre>';
                } else {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<p>Errore: ' + data.error + '</p>';
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>Errore: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
"""

def connect_to_socket(message):
    """Connette al server socket e invia un messaggio"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((SOCKET_HOST, SOCKET_PORT))
            s.send(message.encode())
            
            # Riceve tutti i dati
            data = b""
            s.settimeout(3)  # Timeout per la ricezione
            try:
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        # Il server ha chiuso la connessione, abbiamo tutti i dati
                        break
                    data += chunk
                    # Prova a deserializzare per vedere se abbiamo tutti i dati pickle
                    # (pickle può essere deserializzato solo quando è completo)
                    try:
                        pickle.loads(data)
                        # Se funziona, abbiamo tutti i dati
                        break
                    except (pickle.UnpicklingError, EOFError):
                        # Non abbiamo ancora tutti i dati pickle, continua
                        continue
                    except:
                        # Potrebbe non essere pickle, continua a ricevere
                        pass
            except socket.timeout:
                # Timeout: abbiamo ricevuto tutti i dati disponibili
                pass
            
            # Prova a deserializzare i dati ricevuti
            if data:
                # Prima prova pickle (per risposte BWT)
                try:
                    result, elapsed = pickle.loads(data)
                    return {"type": "pickle", "result": result, "elapsed": elapsed}
                except (pickle.UnpicklingError, EOFError, ValueError):
                    # Non è pickle, prova JSON (per GET_OUTPUT)
                    try:
                        json_data = json.loads(data.decode())
                        return {"type": "json", "data": json_data}
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Non è JSON, prova come stringa semplice
                        try:
                            return {"type": "string", "data": data.decode()}
                        except:
                            return {"type": "error", "message": f"Impossibile decodificare la risposta. Dati ricevuti: {len(data)} bytes"}
                except Exception as e:
                    return {"type": "error", "message": f"Errore nella deserializzazione: {str(e)}"}
            
            return {"type": "error", "message": "Nessuna risposta dal server"}
    except socket.timeout:
        return {"type": "error", "message": "Timeout nella connessione al server"}
    except ConnectionRefusedError:
        return {"type": "error", "message": "Impossibile connettersi al server socket. Assicurati che il server sia in esecuzione."}
    except Exception as e:
        return {"type": "error", "message": f"Errore: {str(e)}"}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/bwt', methods=['POST'])
def api_bwt():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "Stringa vuota"}), 400
        
        print(f"[API] Richiesta BWT per: '{text}'")
        
        # Connetti al server socket e invia il testo
        response = connect_to_socket(text)
        print(f"[API] Risposta dal socket: {response.get('type', 'unknown')}")
        
        if response["type"] == "pickle":
            result_data = {
                "success": True,
                "original": text,
                "result": response["result"],
                "elapsed_time": response["elapsed"]
            }
            print(f"[API] Invio risultato: {result_data}")
            return jsonify(result_data)
        elif response["type"] == "error":
            print(f"[API] Errore: {response['message']}")
            return jsonify({"success": False, "error": response["message"]}), 500
        else:
            print(f"[API] Tipo risposta inatteso: {response.get('type')}")
            return jsonify({"success": False, "error": f"Risposta inattesa dal server: {response.get('type', 'unknown')}"}), 500
            
    except Exception as e:
        print(f"[API] Eccezione: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/output', methods=['GET'])
def api_output():
    try:
        # Connetti al server socket e richiedi output.json
        response = connect_to_socket(KEYWORD_GET_OUTPUT)
        
        if response["type"] == "json":
            return jsonify({
                "success": True,
                "output": response["data"]
            })
        elif response["type"] == "string":
            # Se è una stringa, prova a parsarla come JSON
            try:
                json_data = json.loads(response["data"])
                return jsonify({
                    "success": True,
                    "output": json_data
                })
            except:
                return jsonify({
                    "success": True,
                    "output": response["data"]
                })
        elif response["type"] == "error":
            return jsonify({"success": False, "error": response["message"]}), 500
        else:
            return jsonify({"success": False, "error": "Risposta inattesa dal server"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("Server web avviato su http://127.0.0.1:5000")
    print("Apri il browser e vai su http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5050, debug=True)

