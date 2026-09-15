import sqlite3


def test_seed_crea_solo_dati_dimostrativi(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTROL_ROOM_DEMO_DATA_DIR", str(tmp_path))

    from data.database import inizializza_database, percorso_database
    from demo.seed import popola_demo_se_vuoto

    inizializza_database()
    assert popola_demo_se_vuoto() is True
    assert popola_demo_se_vuoto() is False

    conn = sqlite3.connect(percorso_database())
    try:
        assert conn.execute("SELECT COUNT(*) FROM operatori").fetchone()[0] == 4
        assert conn.execute("SELECT COUNT(*) FROM chiavi").fetchone()[0] == 6
        assert conn.execute("SELECT COUNT(*) FROM radio").fetchone()[0] == 3
        assert conn.execute(
            "SELECT COUNT(*) FROM demo_metadata WHERE chiave = 'dataset_sintetico'"
        ).fetchone()[0] == 1
        testi = " ".join(
            r[0] for r in conn.execute(
                "SELECT nome_canonico || ' ' || cognome_canonico FROM operatori"
            )
        )
        assert "Demo" in testi
    finally:
        conn.close()
