"""Documentazione della versione portfolio."""
from datetime import date, datetime, timedelta

from data.database import ottieni_connessione


def _giorno(offset: int = 0) -> str:
    return (date.today() + timedelta(days=offset)).strftime("%d-%m-%Y")


def popola_demo_se_vuoto() -> bool:
    """Documentazione della versione portfolio."""
    conn = ottieni_connessione()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS demo_metadata (chiave TEXT PRIMARY KEY, valore TEXT NOT NULL)"
        )
        if conn.execute(
            "SELECT 1 FROM demo_metadata WHERE chiave = 'dataset_sintetico'"
        ).fetchone():
            return False
        tabelle = (
            "operatori", "bacheche", "chiavi", "consegne_radio", "radio",
            "oggetti_smarriti", "cassaforte_elementi", "passaggio_consegne",
        )
        if any(conn.execute(f"SELECT COUNT(*) FROM {tabella}").fetchone()[0] for tabella in tabelle):
            return False

        creato_il = datetime.now().strftime("%d-%m-%Y %H:%M")
        operatori = [
            ("Alex", "Demo01", "sala_controllo"),
            ("Sam", "Demo02", "sala_controllo"),
            ("Casey", "Demo03", "gpg"),
            ("Jordan", "Demo04", "manutenzione"),
        ]
        conn.executemany(
            "INSERT INTO operatori (nome_canonico, cognome_canonico, chiave_normalizzata, "
            "categoria_operatore, creato_il, attivo) VALUES (?, ?, ?, ?, ?, 1)",
            [(n, c, f"{n} {c}".casefold(), categoria, creato_il) for n, c, categoria in operatori],
        )
        conn.executemany(
            "INSERT INTO bacheche (nome) VALUES (?)",
            [("Bacheca Demo A",), ("Bacheca Demo B",), ("Bacheca Tecnica Demo",)],
        )
        bacheche = dict(conn.execute("SELECT nome, id FROM bacheche"))
        conn.executemany(
            "INSERT INTO chiavi (bacheca_id, numero, descrizione, blocco) VALUES (?, ?, ?, ?)",
            [
                (bacheche["Bacheca Demo A"], 1, "Ingresso Demo A", "Piano demo 0"),
                (bacheche["Bacheca Demo A"], 2, "Ufficio Demo A1", "Piano demo 1"),
                (bacheche["Bacheca Demo B"], 1, "Magazzino Demo B", "Area demo"),
                (bacheche["Bacheca Demo B"], 2, "Locale tecnico Demo", "Area demo"),
                (bacheche["Bacheca Tecnica Demo"], 1, "Quadro Demo T1", "Tecnica"),
                (bacheche["Bacheca Tecnica Demo"], 2, "Armadio Demo T2", "Tecnica"),
            ],
        )
        prima_chiave = conn.execute("SELECT id FROM chiavi ORDER BY id LIMIT 1").fetchone()[0]
        conn.execute(
            "INSERT INTO chiavi_movimenti (chiave_id, tipo, data, ora, persona, note) "
            "VALUES (?, 'uscita', ?, '09:15', 'Alex Demo01', 'Movimento sintetico')",
            (prima_chiave, _giorno()),
        )
        conn.executemany(
            "INSERT INTO cassaforte_chiavi "
            "(piano, targhetta, area_ufficio, numero_chiavi, colore_targhetta) VALUES (?, ?, ?, ?, ?)",
            [
                ("Demo 0", 101, "Area Demo Alfa", 2, "Blu"),
                ("Demo 1", 102, "Area Demo Beta", 1, "Verde"),
                ("Demo 2", 103, "Area Demo Gamma", 3, "Giallo"),
            ],
        )
        conn.executemany(
            "INSERT INTO cassaforte_elementi (descrizione, categoria, note) VALUES (?, ?, ?)",
            [
                ("Busta documenti DEMO-001", "documenti", "Contenuto fittizio"),
                ("Kit chiavi emergenza DEMO", "chiavi", "Solo dimostrazione"),
                ("Fondo cassa DEMO", "fondo_cassa", "Valore non reale"),
            ],
        )
        for operazione_id, (elemento_id,) in enumerate(
            conn.execute("SELECT id FROM cassaforte_elementi ORDER BY id"), start=1
        ):
            conn.execute(
                "INSERT INTO cassaforte_movimenti "
                "(operazione_id, elemento_id, tipo, data, ora, persona, numero_busta, data_busta, note) "
                "VALUES (?, ?, 'deposito', NULL, NULL, NULL, ?, ?, 'Deposito sintetico')",
                (operazione_id, elemento_id, f"DEMO-B{operazione_id:03d}", _giorno(-7)),
            )
        conn.executemany(
            "INSERT INTO radio (tipo_apparato, selettiva, matricola, custodito_da, assegnata_a, stato, note) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("RADIO DEMO", "D-01", "DEMO-RAD-001", "Control Room", "", "disponibile", "Dato sintetico"),
                ("RADIO DEMO", "D-02", "DEMO-RAD-002", "Control Room", "Casey Demo03", "assegnata", "Dato sintetico"),
                ("BASE DEMO", "D-BASE", "DEMO-BASE-01", "Control Room", "", "disponibile", "Dato sintetico"),
            ],
        )
        conn.executemany(
            "INSERT INTO auricolari_conteggio (modello, stato, quantita) VALUES (?, ?, ?)",
            [("Auricolare Demo", "funzionante", 5), ("Auricolare Demo", "guasto", 1)],
        )
        conn.execute(
            "INSERT INTO consegne_radio "
            "(data, radio_identificativo, ora_consegna, cognome_consegna, auricolare, note) "
            "VALUES (?, 'DEMO-RAD-002', '08:00', 'Demo03', 'Sì', 'Consegna sintetica')",
            (_giorno(),),
        )
        conn.executemany(
            "INSERT INTO oggetti_smarriti "
            "(data_ritiro, ora_ritiro, operatore_ritiro, numero_sigillo, descrizione, "
            "proprietario, ubicazione, stato, note_import) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (_giorno(-1), "15:20", "Alex Demo01", "DEMO-S001", "Zaino dimostrativo", "Utente Demo A", "Scaffale Demo 1", "in_custodia", "Record sintetico"),
                (_giorno(-3), "10:05", "Sam Demo02", "DEMO-S002", "Ombrello dimostrativo", "Utente Demo B", "Scaffale Demo 2", "in_custodia", "Record sintetico"),
            ],
        )
        conn.executemany(
            "INSERT INTO passaggio_consegne (testo, creato_il, fissato) VALUES (?, ?, ?)",
            [
                ("DEMO — verificare il rientro della chiave 1.", f"{_giorno().replace('-', '.')} 09:30", 1),
                ("DEMO — controllo apparati completato.", f"{_giorno().replace('-', '.')} 08:10", 0),
            ],
        )
        conn.execute(
            "INSERT INTO demo_metadata (chiave, valore) VALUES ('dataset_sintetico', '1')"
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
