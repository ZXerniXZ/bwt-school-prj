#!/usr/bin/env python3
"""
Script master per eseguire tutti i test e generare il report finale
"""
import subprocess
import sys
import socket
import time

def check_server():
    """Verifica se il server socket è attivo"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', 65432))
        s.close()
        return result == 0
    except:
        return False

def check_flask():
    """Verifica se Flask è attivo"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:5050/', timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("=" * 80)
    print("ESECUZIONE COMPLETA TEST SISTEMA BWT")
    print("=" * 80)
    
    # Verifica server
    print("\nVerifica server socket...")
    if not check_server():
        print("❌ ERRORE: Server socket non attivo sulla porta 65432")
        print("   Avvia il server prima di eseguire i test:")
        print("   - Se in Docker: sudo docker-compose up -d")
        print("   - Se locale: python3 server.py")
        sys.exit(1)
    print("✅ Server socket attivo")
    
    # Verifica Flask (opzionale per alcuni test)
    print("\nVerifica server Flask...")
    flask_active = check_flask()
    if flask_active:
        print("✅ Server Flask attivo")
    else:
        print("⚠️  Server Flask non attivo (alcuni test potrebbero fallire)")
        print("   Avvia Flask con: python3 client.py")
    
    # Esegui test
    tests = [
        ("Test Scalabilità", "test_scalability.py"),
        ("Test Concorrenza", "test_concurrency.py"),
        ("Test Casi Edge", "test_edge_cases.py"),
        ("Test Persistenza", "test_persistence.py"),
    ]
    
    if flask_active:
        tests.append(("Test Overhead", "test_overhead.py"))
    
    print("\n" + "=" * 80)
    print("ESECUZIONE TEST")
    print("=" * 80)
    
    for test_name, test_file in tests:
        print(f"\n{test_name}...")
        print("-" * 80)
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=300
            )
            print(result.stdout)
            if result.stderr:
                print("Errori:", result.stderr)
            if result.returncode != 0:
                print(f"⚠️  {test_name} completato con errori (codice {result.returncode})")
            else:
                print(f"✅ {test_name} completato")
        except subprocess.TimeoutExpired:
            print(f"❌ {test_name} timeout dopo 5 minuti")
        except Exception as e:
            print(f"❌ Errore eseguendo {test_name}: {e}")
    
    # Genera report
    print("\n" + "=" * 80)
    print("GENERAZIONE REPORT")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, "generate_report.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("\n✅ Report generato con successo: TEST_REPORT.txt")
        else:
            print("⚠️  Report generato con errori")
    except Exception as e:
        print(f"❌ Errore generando report: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETATI")
    print("=" * 80)
    print("\nConsulta TEST_REPORT.txt per i risultati completi.")

if __name__ == '__main__':
    main()

