FROM python:3.11-slim

WORKDIR /app

# Copia i file necessari
COPY server.py .

# Espone la porta del server
EXPOSE 65432

# Abilita output non bufferizzato per vedere i log in tempo reale necessario per la risoluzione di un bug
ENV PYTHONUNBUFFERED=1

# Comando per avviare il server
CMD ["python", "server.py"]

