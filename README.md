# BWT Distributed System: Architetture e Sicurezza
Questo repository ospita lo sviluppo incrementale di un sistema distribuito per il calcolo della **Burrows-Wheeler Transform** (***BWT***), un algoritmo di riorganizzazione dei dati fondamentale per la compressione lossless e la bioinformatica. Il progetto esplora l'evoluzione da un semplice scambio socket a un'infrastruttura containerizzata a tre livelli, analizzando criticamente prestazioni, concorrenza e sicurezza.

# Indice dei Branch (Evoluzione del Progetto)
Il progetto è suddiviso in tre versioni principali, ognuna delle quali introduce nuovi paradigmi architettonici:

• [v0.1](https://github.com/ZXerniXZ/bwt-school-prj/tree/v0.1) - Base Implementation: Implementazione **monolitica** con **comunicazione sincrona e bloccante** tra un singolo client e un server tramite **socket TCP**.

• [v0.2](https://github.com/ZXerniXZ/bwt-school-prj/tree/v0.2)  - **Concurrency & Persistence**: Introduzione del multi-threading per gestire client simultanei e persistenza dello storico delle elaborazioni in formato **JSON**.

•  [v0.3](https://github.com/ZXerniXZ/bwt-school-prj/tree/v0.3)  - Professional Architecture: Modello a tre livelli con un **Bridge Flask (HTTP ↔ socket)**, completa containerizzazione **Docker** e gestione della persistenza tramite volumi.



