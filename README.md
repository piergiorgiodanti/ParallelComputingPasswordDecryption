# Parallel Computing: Password Decryption

Implementazione sequenziale e parallela di un algoritmo di brute force di password decryption.

## 1. Prerequisiti: Installazione di `uv`

Il progetto utilizza **uv** per la gestione dell'ambiente e delle dipendenze. Se non è già installato nel sistema, procedere con i seguenti comandi:

* **macOS / Linux:**
  ```bash
  curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
  ```
* **Windows (PowerShell):**
  ```powershell
  powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
  ```

## 2. Configurazione ed Esecuzione

A seconda del sistema operativo utilizzato, aprire il terminale nella cartella radice del progetto ed eseguire i comandi in sequenza.

### macOS / Linux

```bash
# 1. Installazione versione di Python
uv python install 3.14+freethreaded

# 2. Creazione dell'ambiente virtuale
uv venv -p 3.14+freethreaded

# 3. Attivazione dell'ambiente virtuale
source .venv/bin/activate

# 4. Esecuzione (con GIL disabilitato)
uv run -p 3.14+freethreaded python -X gil=0 src/main.py
```

### Windows

```powershell
# 1. Installazione versione di Python
uv python install 3.14+freethreaded

# 2. Creazione dell'ambiente virtuale
uv venv -p 3.14+freethreaded

# 3. Attivazione dell'ambiente virtuale
.venv\Scripts\activate

# 4. Esecuzione (con GIL disabilitato)
uv run -p 3.14+freethreaded python -X gil=0 src/main.py
```

---
**Nota:** Il flag `-X gil=0` utilizzato in fase di esecuzione garantisce che l'interprete Python venga avviato disabilitando il Global Interpreter Lock (GIL), consentendo il reale parallelismo dei thread.
