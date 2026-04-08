# Parallel Computing: Password Decryption

Implementazione sequenziale e parallela di un algoritmo di brute force per la decrittazione di password, sviluppata in Python 3.14 (no-GIL) con **Multithreading**.

## Prerequisiti

Il progetto utilizza **uv** per la gestione dell'ambiente e delle dipendenze. Per installare:

* **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
* **Windows:**
  ```powershell
  powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
  ```

## Configurazione ed Esecuzione
### macOS / Linux

```bash
# Installazione versione di Python
uv python install 3.14+freethreaded

# Creazione dell'ambiente virtuale
uv venv -p 3.14+freethreaded

# Attivazione dell'ambiente virtuale
source .venv/bin/activate

# Esecuzione demo (con GIL disabilitato)
uv run -p 3.14+freethreaded python -X gil=0 src/main.py demo

# Esecuzione benchmarks (con GIL disabilitato)
uv run -p 3.14+freethreaded python -X gil=0 src/main.py benchmarks
```

### Windows

```powershell
# Installazione versione di Python
uv python install 3.14+freethreaded

# Creazione dell'ambiente virtuale
uv venv -p 3.14+freethreaded

# Attivazione dell'ambiente virtuale
.venv\Scripts\activate

# Esecuzione demo (con GIL disabilitato)
uv run -p 3.14+freethreaded python -X gil=0 src/main.py demo

# Esecuzione benchmarks (con GIL disabilitato)
uv run -p 3.14+freethreaded python -X gil=0 src/main.py benchmarks
```

---
**Nota:** Il flag `-X gil=0` utilizzato in fase di esecuzione garantisce che l'interprete Python venga avviato disabilitando il GIL, rendendo possibile l'utilizzo del multithreading.

## Grafici
Dopo aver raccolto i dati (che verranno salvati in `results/dumps/`), generare i plot con:
```bash
cd utils
uv run python plots.py
```
