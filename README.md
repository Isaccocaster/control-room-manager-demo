# Control Room Manager Demo

Applicazione desktop dimostrativa per coordinare le attività quotidiane di una
control room: chiavi, apparati radio, oggetti rinvenuti, consegne di turno,
cassaforte e rapporti giornalieri.

Questa repository è una versione portfolio. Non contiene database, backup,
nomi, percorsi, fotografie, documenti o configurazioni provenienti da un
ambiente operativo. Al primo avvio viene creato localmente un piccolo dataset
marcato **DEMO**.

## Funzionalità

- anagrafica degli operatori con categorie e disattivazione logica;
- inventario e movimentazione delle chiavi;
- consegna e inventario degli apparati radio;
- gestione di oggetti rinvenuti e relativo stato;
- registro della cassaforte con storico append-only;
- passaggio di consegne e calendario operativo;
- esportazioni Excel e gestione dei rapporti giornalieri;
- database SQLite con vincoli, transazioni e versione dello schema;
- registri tecnici, backup atomici e controlli di integrità.

## Tecnologie

- Python 3.11+
- PySide6
- SQLite / SQL
- openpyxl
- python-docx
- pytest

## Avvio rapido

```bash
python -m venv .venv
```

Su Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Su Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Il database dimostrativo viene creato in `demo_data/` e non deve essere
committato. Per ripartire da zero è sufficiente chiudere l'applicazione e
eliminare localmente quella cartella.

## Test

```bash
pytest -q
```

## Struttura

```text
config/      configurazione, versionamento e logging
data/        persistenza SQLite e logica di dominio
demo/        generazione del dataset sintetico
documents/   esportazioni Word ed Excel
ui/          interfaccia PySide6
tests/       controlli specifici della versione demo
```

## Privacy

I dati inclusi sono inventati e riconoscibili dai prefissi `DEMO` o dai nomi
`Demo01`, `Demo02`, ecc. Prima di pubblicare nuove modifiche, eseguire sempre i
controlli descritti in [PRIVACY.md](PRIVACY.md).

## Nota

Il progetto nasce come esercizio pratico di analisi dei requisiti e sviluppo
di uno strumento desktop. La versione pubblica è intenzionalmente separata da
qualunque installazione reale.

## Autore

Sviluppato da **Antonino Todaro** come progetto portfolio durante il percorso
di studi in Informatica (L-31).

## Licenza

Distribuito con licenza [MIT](LICENSE).
