#!/usr/bin/env python3
"""
Test Overhead Bridge - Confronta latenza Socket diretto vs HTTP Flask
"""
import socket
import pickle
import time
import requests
import statistics

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432
FLASK_URL = "http://127.0.0.1:5050/api/bwt"

def test_socket_direct(text, iterations=10):
    """Test diretto via socket"""
    times = []
    
    for _ in range(iterations):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                
                start = time.perf_counter()
                s.connect((SOCKET_HOST, SOCKET_PORT))
                s.send(text.encode())
                
                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    try:
                        result, server_time = pickle.loads(data)
                        break
                    except (pickle.UnpicklingError, EOFError):
                        continue
                
                end = time.perf_counter()
                total_time = end - start
                times.append({
                    'total': total_time,
                    'server': server_time,
                    'overhead': total_time - server_time
                })
        except Exception as e:
            print(f"Errore socket: {e}")
            return None
    
    return times

def test_flask_http(text, iterations=10):
    """Test via Flask HTTP"""
    times = []
    
    for _ in range(iterations):
        try:
            start = time.perf_counter()
            response = requests.post(FLASK_URL, 
                                   json={'text': text},
                                   timeout=10)
            end = time.perf_counter()
            
            if response.status_code == 200:
                data = response.json()
                total_time = end - start
                server_time = data.get('elapsed_time', 0)
                
                times.append({
                    'total': total_time,
                    'server': server_time,
                    'overhead': total_time - server_time
                })
        except Exception as e:
            print(f"Errore HTTP: {e}")
            return None
    
    return times

def run_overhead_test():
    """Esegue test di overhead"""
    print("=" * 60)
    print("TEST OVERHEAD BRIDGE - Socket vs HTTP")
    print("=" * 60)
    
    test_strings = [
        ("banana", "Stringa corta"),
        ("a" * 100, "Stringa media (100 char)"),
        ("a" * 1000, "Stringa lunga (1000 char)"),
    ]
    
    all_results = []
    
    for text, desc in test_strings:
        print(f"\n{desc}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print("-" * 60)
        
        # Test Socket
        print("Test Socket diretto (10 iterazioni)...")
        socket_times = test_socket_direct(text, 10)
        
        if socket_times:
            socket_avg_total = statistics.mean([t['total'] for t in socket_times])
            socket_avg_server = statistics.mean([t['server'] for t in socket_times])
            socket_avg_overhead = statistics.mean([t['overhead'] for t in socket_times])
            
            print(f"  Tempo totale medio: {socket_avg_total:.6f}s")
            print(f"  Tempo server medio: {socket_avg_server:.6f}s")
            print(f"  Overhead medio:     {socket_avg_overhead:.6f}s")
        else:
            print("  ❌ Errore nel test socket")
            continue
        
        # Test Flask HTTP
        print("\nTest Flask HTTP (10 iterazioni)...")
        flask_times = test_flask_http(text, 10)
        
        if flask_times:
            flask_avg_total = statistics.mean([t['total'] for t in flask_times])
            flask_avg_server = statistics.mean([t['server'] for t in flask_times])
            flask_avg_overhead = statistics.mean([t['overhead'] for t in flask_times])
            
            print(f"  Tempo totale medio: {flask_avg_total:.6f}s")
            print(f"  Tempo server medio: {flask_avg_server:.6f}s")
            print(f"  Overhead medio:     {flask_avg_overhead:.6f}s")
        else:
            print("  ❌ Errore nel test HTTP")
            continue
        
        # Confronto
        overhead_diff = flask_avg_overhead - socket_avg_overhead
        overhead_percent = (overhead_diff / socket_avg_total * 100) if socket_avg_total > 0 else 0
        
        print(f"\nConfronto:")
        print(f"  Differenza overhead: {overhead_diff:.6f}s")
        print(f"  Percentuale extra:   {overhead_percent:.2f}%")
        
        all_results.append({
            'description': desc,
            'text_length': len(text),
            'socket': {
                'avg_total': socket_avg_total,
                'avg_server': socket_avg_server,
                'avg_overhead': socket_avg_overhead
            },
            'flask': {
                'avg_total': flask_avg_total,
                'avg_server': flask_avg_server,
                'avg_overhead': flask_avg_overhead
            },
            'overhead_diff': overhead_diff,
            'overhead_percent': overhead_percent
        })
    
    return all_results

if __name__ == '__main__':
    results = run_overhead_test()
    
    # Salva risultati
    import json
    with open('test_results_overhead.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Risultati salvati in test_results_overhead.json")

