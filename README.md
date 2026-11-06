# Control Room Manager · Demo

**Applicazione desktop in Python per digitalizzare la gestione operativa di una sala controllo.**

Lavoro da oltre sei anni come operatore di sala controllo in ambienti H24. Molte attività quotidiane (movimentazione delle chiavi, consegna delle radio, oggetti rinvenuti, passaggio di consegne tra i turni, rapporti giornalieri) si gestivano ancora su carta o su fogli Excel sparsi. Ho progettato e sviluppato questa applicazione per riunirle in un unico strumento, con uno storico consultabile e i report generati in automatico.

> Questa è la **versione portfolio**: contiene solo dati inventati, marcati `DEMO`, ed è separata da qualunque installazione reale. Dettagli in [PRIVACY.md](PRIVACY.md) e [SANITIZATION.md](SANITIZATION.md).

**🌐 Language:** [Italiano](#funzionalità) | [English](#english)

---

## Funzionalità

| Modulo | Cosa fa |
|---|---|
| **Anagrafica operatori** | Elenco del personale per categoria, con disattivazione logica (lo storico non si perde) |
| **Bacheca chiavi** | Inventario delle chiavi per bacheca, registrazione di uscite e rientri |
| **Gestione e consegna radio** | Inventario degli apparati, assegnazioni, consegne giornaliere e auricolari |
| **Oggetti rinvenuti** | Registrazione con sigillo, ubicazione e stato fino alla riconsegna |
| **Cassaforte** | Registro di depositi e prelievi con storico *append-only* (non modificabile) |
| **Passaggio di consegne** | Note tra un turno e l'altro, con messaggi fissati in evidenza |
| **Calendario operativo** | Si sceglie un giorno e si vede tutto ciò che è successo, raggruppato per modulo |
| **Rapporti giornalieri** | Editor dei rapporti di turno con archivio per anno e mese, salvataggio protetto ed esportazione in Word |
| **Esportazioni** | Prospetti Excel per chiavi, radio, cassaforte, oggetti rinvenuti e consegne |
| **Diagnostica** | Stato di database e backup visibile dall'interfaccia, con controllo approfondito su richiesta |

## Punti tecnici

- **Database SQLite** con chiavi esterne attive, vincoli e transazioni.
- **Versionamento dello schema** tramite `PRAGMA user_version`: all'avvio il programma riconosce un database creato da una versione più recente e si ferma con un messaggio chiaro, invece di rischiare di danneggiare i dati.
- **Backup atomici e versionati**: la copia viene scritta in un file temporaneo, verificata con `PRAGMA integrity_check` e solo dopo sostituita con `os.replace`, così un'interruzione a metà non lascia mai un backup corrotto.
- **Gestione degli errori a due livelli**: ogni modulo gestisce i propri casi specifici (un file Excel aperto, un rapporto non leggibile) e un gestore globale intercetta l'imprevisto. L'utente vede un messaggio comprensibile, il dettaglio tecnico finisce nel registro.
- **Registro tecnico** (logging) di avvio, chiusura ed errori, utile anche quando il programma è distribuito come eseguibile.
- **Report automatici** in Word (`python-docx`) ed Excel (`openpyxl`).
- **Architettura a livelli**: dati, documenti e interfaccia sono separati in pacchetti distinti.
- **Test automatici** con `pytest` su un database temporaneo isolato.

## Tecnologie

Python 3.11+ · PySide6 (Qt) · SQLite / SQL · openpyxl · python-docx · pytest

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

Al primo avvio viene creato in `demo_data/` un piccolo database con dati fittizi (operatori `Demo01`, `Demo02`…, chiavi e radio `DEMO-…`). Per ripartire da zero basta chiudere l'applicazione ed eliminare quella cartella.

## Test

```bash
pytest -q
```

## Struttura del progetto

```text
config/      configurazione, versionamento e registro tecnico
data/        persistenza SQLite e logica di dominio (un modulo per area)
demo/        generazione del dataset fittizio
documents/   esportazioni Word ed Excel
ui/          interfaccia PySide6, una cartella per schermata
tests/       test automatici
```

## Privacy

I dati inclusi sono inventati e riconoscibili dal prefisso `DEMO`. Database, backup, log ed esportazioni generati durante l'uso sono esclusi da Git tramite `.gitignore`. Prima di pubblicare nuove modifiche vanno eseguiti i controlli descritti in [PRIVACY.md](PRIVACY.md).

---

## English

**Desktop application (Python, PySide6, SQLite) that digitalises the daily operations of a security control room:** key tracking, radio equipment, lost & found, shift handovers, safe log and daily reports, with automatic Word/Excel exports.

I built it starting from my own experience as a 24/7 control room operator. Technical highlights: SQLite with foreign keys and schema versioning (`PRAGMA user_version`), atomic and verified backups (`integrity_check` + `os.replace`), layered architecture, two-level error handling with technical logging, and automated tests with `pytest`.

This public version contains **only synthetic data** marked `DEMO`. To run it: create a virtual environment, `pip install -r requirements.txt`, then `python main.py`.

---

## Autore

Sviluppato da **Antonino Todaro** come progetto portfolio durante il percorso di studi in Informatica (L-31) · [github.com/Isaccocaster](https://github.com/Isaccocaster)

## Licenza

Distribuito con licenza [MIT](LICENSE).
