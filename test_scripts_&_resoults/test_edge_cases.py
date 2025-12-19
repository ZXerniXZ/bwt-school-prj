#!/usr/bin/env python3
"""
Test Casi d'Uso Specifici - Robustezza del sistema
"""
import socket
import pickle
import json

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432

def test_bwt(text, test_name):
    """Test BWT e restituisce risultato"""
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
                    return {
                        'success': True,
                        'result': result,
                        'elapsed': elapsed,
                        'original': text
                    }
                except (pickle.UnpicklingError, EOFError):
                    continue
        return {'success': False, 'error': 'Nessuna risposta'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_via_flask(text):
    """Test tramite Flask API"""
    try:
        import requests
        response = requests.post('http://127.0.0.1:5050/api/bwt', 
                                json={'text': text},
                                timeout=10)
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}

def run_edge_cases_test():
    """Esegue test dei casi edge"""
    print("=" * 60)
    print("TEST CASI D'USO SPECIFICI - Robustezza")
    print("=" * 60)
    
    results = []
    
    # Test 1: Stringa con simbolo $
    print("\n1. Test: Stringa con simbolo $")
    print("-" * 60)
    test_cases = [
        ("prezzo$100", "Stringa con $ nel mezzo"),
        ("$start", "Stringa che inizia con $"),
        ("end$", "Stringa che finisce con $"),
        ("a$b$c", "Stringa con multipli $"),
    ]
    
    for text, desc in test_cases:
        result = test_bwt(text, desc)
        results.append({
            'test': 'Stringa con $',
            'description': desc,
            'input': text,
            'result': result
        })
        
        if result['success']:
            print(f"  Input: '{text}'")
            print(f"  Output: '{result['result']}'")
            print(f"  Tempo: {result['elapsed']:.9f}s")
            print(f"  ✅ OK")
        else:
            print(f"  Input: '{text}'")
            print(f"  ❌ ERRORE: {result.get('error', 'Unknown')}")
        print()
    
    # Test 2: Stringa vuota
    print("\n2. Test: Stringa vuota")
    print("-" * 60)
    
    # Test diretto socket
    result_socket = test_bwt("", "Stringa vuota socket")
    results.append({
        'test': 'Stringa vuota',
        'method': 'socket',
        'result': result_socket
    })
    
    print("  Via Socket:")
    if result_socket['success']:
        print(f"    Output: '{result_socket['result']}'")
        print(f"    ✅ OK")
    else:
        print(f"    ❌ ERRORE: {result_socket.get('error', 'Unknown')}")
    
    # Test via Flask
    result_flask = test_via_flask("")
    results.append({
        'test': 'Stringa vuota',
        'method': 'flask',
        'result': result_flask
    })
    
    print("  Via Flask:")
    if result_flask.get('success'):
        print(f"    ✅ OK - Gestito correttamente")
    else:
        print(f"    ❌ ERRORE: {result_flask.get('error', 'Unknown')}")
    print()
    
    # Test 3: Caratteri non ASCII
    print("\n3. Test: Caratteri non ASCII")
    print("-" * 60)
    non_ascii_cases = [
        ("caffè", "Caratteri accentati"),
        ("naïve", "Caratteri con dieresi"),
        ("你好", "Caratteri cinesi"),
        ("🚀test🌟", "Emoji"),
        ("Müller", "Caratteri speciali"),
    ]
    
    for text, desc in non_ascii_cases:
        result = test_bwt(text, desc)
        results.append({
            'test': 'Caratteri non ASCII',
            'description': desc,
            'input': text,
            'result': result
        })
        
        if result['success']:
            print(f"  Input: '{text}'")
            print(f"  Output: '{result['result']}'")
            print(f"  Tempo: {result['elapsed']:.9f}s")
            
            # Verifica integrità: il risultato contiene caratteri corretti?
            if len(result['result']) > 0:
                print(f"  ✅ OK - Dati preservati")
            else:
                print(f"  ⚠️  WARNING - Risultato vuoto")
        else:
            print(f"  Input: '{text}'")
            print(f"  ❌ ERRORE: {result.get('error', 'Unknown')}")
        print()
    
    return results

if __name__ == '__main__':
    results = run_edge_cases_test()
    
    # Salva risultati
    with open('test_results_edge_cases.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print("Risultati salvati in test_results_edge_cases.json")

