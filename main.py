"""Documentazione della versione portfolio."""
import sys
import traceback

import PySide6
from PySide6.QtWidgets import QApplication, QMessageBox

from config.registro import (
    configura as configura_registro,
    imposta_fornitore_versione_libreria_ui,
    logger,
    registra_avvio,
    registra_avvio_completato,
    registra_chiusura,
    registra_eccezione_non_gestita,
)
from data.database import inizializza_database
from demo.seed import popola_demo_se_vuoto
from data.schema import ErroreSchemaNonSupportato
from ui.finestra_principale import FinestraPrincipale
from ui.tema import FOGLIO_DI_STILE

_registro = logger(__name__)


def gestore_eccezioni_globale(tipo, valore, tb) -> None:
    """Documentazione della versione portfolio."""
    registra_eccezione_non_gestita(tipo, valore, tb)
    traceback.print_exception(tipo, valore, tb, file=sys.stderr)
    try:
        QMessageBox.critical(
            None, "Errore imprevisto",
            "Si è verificato un errore imprevisto. Il programma resta aperto: "
            "puoi continuare a lavorare, ma se l'ultima operazione non sembra "
            "riuscita riprova.\n\n"
            f"Dettaglio: {valore}",
        )
    except Exception:
        pass


def _prepara_database() -> bool:
    """Documentazione della versione portfolio."""
    try:
        inizializza_database()
        popola_demo_se_vuoto()
    except ErroreSchemaNonSupportato as errore:
        _registro.critical("Avvio interrotto: %s", errore)
        QMessageBox.critical(None, "Versione non compatibile", errore.messaggio_operatore)
        return False
    except Exception as errore:
        _registro.critical("Avvio interrotto: database non utilizzabile", exc_info=True)
        QMessageBox.critical(
            None, "Database non utilizzabile",
            "Non è stato possibile aprire il database di Control Room Manager Demo.\n\n"
            "I dati non sono stati modificati. Contatta l'ufficio IT: nella "
            "cartella dei registri tecnici c'è il dettaglio di cosa è successo."
            f"\n\nDettaglio: {errore}",
        )
        return False

    from config.registro import registra_schema
    from data.database import versione_schema_corrente

    registra_schema(versione_schema_corrente())
    return True


def main():


    configura_registro()
    imposta_fornitore_versione_libreria_ui(lambda: PySide6.__version__)
    sys.excepthook = gestore_eccezioni_globale
    registra_avvio()

    app = QApplication(sys.argv)
    app.setStyleSheet(FOGLIO_DI_STILE)


    if not _prepara_database():
        return 2

    finestra = FinestraPrincipale()
    finestra.showMaximized()
    registra_avvio_completato()

    codice = app.exec()
    registra_chiusura(f"chiusura normale (codice {codice})")
    return codice


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:


        logger("avvio").critical("Avvio fallito", exc_info=True)
        raise
