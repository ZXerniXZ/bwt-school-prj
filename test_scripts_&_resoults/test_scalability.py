#!/usr/bin/env python3
"""
Test di Scalabilità - Misura tempi di esecuzione BWT
per stringhe di lunghezza crescente
"""
import socket
import pickle
import time
import string
import random

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 65432

def generate_string(length):
    """Genera una stringa casuale di lunghezza specificata"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_bwt_direct(text):
    """Test diretto via socket"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((SOCKET_HOST, SOCKET_PORT))
            
            start = time.perf_counter()
            s.send(text.encode())
            
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                try:
                    result, elapsed = pickle.loads(data)
                    break
                except (pickle.UnpicklingError, EOFError):
                    continue
            
            end = time.perf_counter()
            total_time = end - start
            return total_time, elapsed
    except Exception as e:
        return None, str(e)

def run_scalability_test():
    """Esegue test di scalabilità"""
    lengths = [10, 100, 500, 1000, 2000, 5000]
    results = []
    
    print("=" * 60)
    print("TEST DI SCALABILITÀ - BWT Algorithm")
    print("=" * 60)
    print(f"{'Lunghezza':<12} {'Tempo Server (s)':<18} {'Tempo Totale (s)':<18} {'O(n²log n)':<15}")
    print("-" * 60)
    
    for length in lengths:
        test_string = generate_string(length)
        
        # Esegui 3 test e prendi la media
        times_server = []
        times_total = []
        
        for _ in range(3):
            total_time, server_time = test_bwt_direct(test_string)
            if total_time is not None:
                times_server.append(server_time)
                times_total.append(total_time)
        
        if times_server:
            avg_server = sum(times_server) / len(times_server)
            avg_total = sum(times_total) / len(times_total)
            
            # Calcola complessità teorica O(n²log n) normalizzata
            n2logn = (length ** 2) * (length.bit_length() if length > 0 else 1)
            
            results.append({
                'length': length,
                'server_time': avg_server,
                'total_time': avg_total,
                'n2logn': n2logn
            })
            
            print(f"{length:<12} {avg_server:<18.9f} {avg_total:<18.9f} {n2logn:<15}")
        else:
            print(f"{length:<12} {'ERROR':<18} {'ERROR':<18}")
    
    print("=" * 60)
    return results

if __name__ == '__main__':
    results = run_scalability_test()
    
    # Salva risultati
    import json
    with open('test_results_scalability.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nRisultati salvati in test_results_scalability.json")

