"""Documentazione della versione portfolio."""
from PySide6.QtCore import QStringListModel, Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from data.operatori import (
    CATEGORIE_OPERATORE,
    ETICHETTE_CATEGORIE_OPERATORE,
    cerca_operatori,
    nome_completo,
    registra_operatore,
    riattiva_operatore,
    trova_operatore,
    trova_operatore_per_nome_completo,
)


def applica_autocomplete_operatori(campo: QLineEdit, categoria: str | None = None) -> None:
    """Documentazione della versione portfolio."""
    completatore = QCompleter(campo)
    completatore.setCaseSensitivity(Qt.CaseInsensitive)
    completatore.setFilterMode(Qt.MatchContains)
    campo.setCompleter(completatore)

    def aggiorna_suggerimenti(testo: str) -> None:
        nomi = [nome_completo(o) for o in cerca_operatori(testo, categoria=categoria)]
        completatore.setModel(QStringListModel(nomi, completatore))

    aggiorna_suggerimenti(campo.text())
    campo.textEdited.connect(aggiorna_suggerimenti)


def applica_autocomplete_operatore_doppio(
    campo_nome: QLineEdit, campo_cognome: QLineEdit, categoria: str | None = None,
) -> None:
    """Documentazione della versione portfolio."""
    completatori = []
    for campo in (campo_nome, campo_cognome):
        completatore = QCompleter(campo)
        completatore.setCaseSensitivity(Qt.CaseInsensitive)
        completatore.setFilterMode(Qt.MatchContains)
        campo.setCompleter(completatore)
        completatori.append(completatore)
    completatore_nome, completatore_cognome = completatori

    def aggiorna_suggerimenti(testo: str) -> None:
        nomi = [nome_completo(o) for o in cerca_operatori(testo, categoria=categoria)]
        completatore_nome.setModel(QStringListModel(nomi, completatore_nome))
        completatore_cognome.setModel(QStringListModel(nomi, completatore_cognome))

    def compila_da_selezione(testo_selezionato: str) -> None:
        corrispondente = next(
            (o for o in cerca_operatori(testo_selezionato, categoria=categoria)
             if nome_completo(o) == testo_selezionato),
            None,
        )
        if corrispondente is None:
            return

        def applica():
            campo_nome.setText(corrispondente["nome_canonico"])
            campo_cognome.setText(corrispondente["cognome_canonico"])


        QTimer.singleShot(0, applica)

    aggiorna_suggerimenti("")
    campo_nome.textEdited.connect(aggiorna_suggerimenti)
    campo_cognome.textEdited.connect(aggiorna_suggerimenti)
    completatore_nome.activated.connect(compila_da_selezione)
    completatore_cognome.activated.connect(compila_da_selezione)


def _suddividi_suggerimento(testo: str) -> tuple[str, str]:
    """Documentazione della versione portfolio."""
    parti = testo.strip().split(" ", 1)
    if len(parti) == 1:
        return "", parti[0]
    return parti[0], parti[1]


class _DialogoNuovoOperatore(QDialog):
    """Documentazione della versione portfolio."""

    def __init__(self, parent, nome_suggerito: str = "", cognome_suggerito: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Nuovo operatore")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        avviso = QLabel("Operatore non presente nell'anagrafica. Registrarlo come nuovo operatore?")
        avviso.setWordWrap(True)
        layout.addWidget(avviso)

        modulo = QFormLayout()
        self.campo_nome = QLineEdit(nome_suggerito)
        modulo.addRow("Nome:", self.campo_nome)
        self.campo_cognome = QLineEdit(cognome_suggerito)
        modulo.addRow("Cognome:", self.campo_cognome)

        self.campo_categoria = QComboBox()


        self.campo_categoria.addItem("— Seleziona categoria —", None)
        for codice in CATEGORIE_OPERATORE:
            self.campo_categoria.addItem(ETICHETTE_CATEGORIE_OPERATORE[codice], codice)
        modulo.addRow("Categoria:", self.campo_categoria)
        layout.addLayout(modulo)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self._al_conferma)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def _al_conferma(self):
        if not self.campo_cognome.text().strip():
            QMessageBox.warning(self, "Dati mancanti", "Il cognome dell'operatore è obbligatorio.")
            return
        if self.campo_categoria.currentData() is None:
            QMessageBox.warning(self, "Categoria mancante", "Seleziona una categoria per il nuovo operatore.")
            return
        self.accept()


def _proponi_riattivazione(parent, operatore: dict) -> bool:
    """Documentazione della versione portfolio."""
    risposta = QMessageBox.question(
        parent, "Operatore disattivato",
        f"\"{nome_completo(operatore)}\" è presente in anagrafica ma risulta disattivato.\n"
        "Vuoi riattivarlo?",
        QMessageBox.Yes | QMessageBox.No,
    )
    if risposta != QMessageBox.Yes:
        return False
    riattiva_operatore(operatore["id"])
    return True


def _registra_da_dialogo(parent, nome_suggerito: str, cognome_suggerito: str) -> dict | None:
    """Documentazione della versione portfolio."""
    finestra = _DialogoNuovoOperatore(parent, nome_suggerito, cognome_suggerito)
    if finestra.exec() != QDialog.Accepted:
        return None
    return registra_operatore(
        finestra.campo_nome.text(), finestra.campo_cognome.text(),
        finestra.campo_categoria.currentData(),
    )


def risolvi_operatore_confermato(parent, nome_digitato: str) -> str | None:
    """Documentazione della versione portfolio."""
    nome_digitato = (nome_digitato or "").strip()
    if not nome_digitato:
        return nome_digitato

    esistente = trova_operatore_per_nome_completo(nome_digitato)
    if esistente is not None:
        if esistente["attivo"]:
            return nome_completo(esistente)
        return nome_completo(esistente) if _proponi_riattivazione(parent, esistente) else None

    nome_sugg, cognome_sugg = _suddividi_suggerimento(nome_digitato)
    nuovo = _registra_da_dialogo(parent, nome_sugg, cognome_sugg)
    return nome_completo(nuovo) if nuovo is not None else None


def risolvi_operatore_nome_cognome_confermato(parent, nome: str, cognome: str):
    """Documentazione della versione portfolio."""
    nome, cognome = (nome or "").strip(), (cognome or "").strip()
    if not cognome:
        return (nome, cognome, None)

    esistente = trova_operatore(nome, cognome)
    if esistente is not None:
        if not esistente["attivo"] and not _proponi_riattivazione(parent, esistente):
            return None
        return (esistente["nome_canonico"], esistente["cognome_canonico"], esistente["id"])

    nuovo = _registra_da_dialogo(parent, nome, cognome)
    if nuovo is None:
        return None
    return (nuovo["nome_canonico"], nuovo["cognome_canonico"], nuovo["id"])


class _DialogoNomeOperatore(QDialog):
    def __init__(self, parent, titolo: str, messaggio: str, valore_iniziale: str = ""):
        super().__init__(parent)
        self.setWindowTitle(titolo)
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(messaggio))

        self.campo = QLineEdit(valore_iniziale)
        applica_autocomplete_operatori(self.campo)
        layout.addWidget(self.campo)

        pulsanti = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)


def richiedi_nome_operatore(parent, titolo: str, messaggio: str, valore_iniziale: str = "") -> str | None:
    """Documentazione della versione portfolio."""
    finestra = _DialogoNomeOperatore(parent, titolo, messaggio, valore_iniziale)
    if finestra.exec() != QDialog.Accepted:
        return None
    testo = finestra.campo.text().strip()
    if not testo:
        return None
    return risolvi_operatore_confermato(parent, testo)
