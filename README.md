# Parallel Computing: Password Decryption
Implementazione sequenziale e parallela di un algoritmo di brute force di password decryption.

## Configurazione ed Esecuzione
- Installazione versione di Python: `uv python install 3.14+freethreaded`
- Creazione dell'ambiente virtuale: `uv venv -p 3.14+freethreaded`
- Attivazione dell'ambiente virtuale: `source .venv/bin/activate`
- Esecuzione: `uv run -p 3.14+freethreaded python -X gil=0 src/main.py`
