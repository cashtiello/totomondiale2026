"""
calcolo_eliminatorie.py
Calcola i punti delle fasi eliminatorie leggendo i JSON centralizzati.
"""

import re
from src.utils import confronta_squadre, normalizza_risultato, calcola_esito_da_risultato
from src.config import PUNTI_ESITO, PUNTI_RISULTATO_ESATTO, PUNTI_MARCATORE
from src.logger import get_logger

log = get_logger(__name__)

FASI_ORDINE = ["sedicesimi", "ottavi", "quarti", "semifinali", "finale"]

FASI_LABEL = {
    "sedicesimi":  "⚔️ Sedicesimi",
    "ottavi":      "🏆 Ottavi",
    "quarti":      "🎯 Quarti",
    "semifinali":  "🔥 Semifinali",
    "finale":      "🥇 Finale",
}


def _calcola_partita(pron: dict, ris_reale: dict) -> dict:
    """Calcola esito/risultato/marcatore per una singola partita eliminatoria."""
    r_real = normalizza_risultato(ris_reale.get("risultato", ""))
    esito_reale = ris_reale.get("esito") or calcola_esito_da_risultato(r_real)
    marcatori_reali_str = ris_reale.get("marcatori", "") or ""

    esito_pron = pron.get("esito")
    esito_ok = bool(esito_pron and esito_reale and esito_pron == esito_reale)

    r_pron = normalizza_risultato(pron.get("risultato", ""))
    risultato_ok = bool(r_pron and r_real and r_pron == r_real)

    marcatore_pron = pron.get("marcatore")
    marcatore_ok = False

    if r_real == "0-0" and not (marcatore_pron or "").strip():
        marcatore_ok = True
    elif marcatore_pron and marcatori_reali_str:
        for mr in [m.strip() for m in marcatori_reali_str.split(",") if m.strip()]:
            mr_pulito = re.sub(r"\s+\d+(\+\d+)?'?$", "", mr).strip()
            if confronta_squadre(marcatore_pron, mr_pulito):
                marcatore_ok = True
                break

    return {
        "esito_ok": esito_ok,
        "risultato_ok": risultato_ok,
        "marcatore_ok": marcatore_ok,
        "risultato_reale": ris_reale.get("risultato", ""),
        "marcatori_reali": marcatori_reali_str,
    }


def calcola_eliminatorie_partecipante(
    nome_completo: str,
    eliminatorie: dict,
) -> dict:
    """
    Calcola punti e dettaglio per tutte le fasi eliminatorie di un partecipante.
    eliminatorie: {fase: {nome_completo: {partite: [...], risultati: {...}}}}
    Restituisce: {fase: {punti, dettaglio_partite}}
    """
    risultato = {}

    for fase in FASI_ORDINE:
        fase_data = eliminatorie.get(fase, {})
        if not fase_data:
            continue

        # Pronostici del partecipante
        partecipante_data = fase_data.get("pronostici", {}).get(nome_completo)
        if not partecipante_data:
            continue

        # Risultati reali della fase
        risultati_reali = fase_data.get("risultati", {})

        pt_esito = pt_ris = pt_marc = 0
        n_esiti = n_ris = n_marc = 0
        dettaglio = []

        for pron in partecipante_data.get("partite", []):
            incontro = pron.get("incontro", "")

            # Trova risultato reale
            ris_reale = None
            for key, ris in risultati_reali.items():
                if confronta_squadre(incontro, key):
                    ris_reale = ris
                    break

            if not ris_reale or not ris_reale.get("risultato"):
                dettaglio.append({
                    "incontro": incontro,
                    "casa": pron.get("casa", ""),
                    "ospite": pron.get("ospite", ""),
                    "giocata": False,
                    "esito_pron": pron.get("esito") or "—",
                    "risultato_pron": pron.get("risultato") or "—",
                    "marcatore_pron": pron.get("marcatore") or "—",
                    "esito_ok": False,
                    "risultato_ok": False,
                    "marcatore_ok": False,
                    "risultato_reale": None,
                    "marcatori_reali": None,
                })
                continue

            calc = _calcola_partita(pron, ris_reale)

            if calc["esito_ok"]:
                pt_esito += PUNTI_ESITO
                n_esiti += 1
            if calc["risultato_ok"]:
                pt_ris += PUNTI_RISULTATO_ESATTO
                n_ris += 1
            if calc["marcatore_ok"]:
                pt_marc += PUNTI_MARCATORE
                n_marc += 1

            dettaglio.append({
                "incontro": incontro,
                "casa": pron.get("casa", ""),
                "ospite": pron.get("ospite", ""),
                "giocata": True,
                "esito_pron": pron.get("esito") or "—",
                "risultato_pron": pron.get("risultato") or "—",
                "marcatore_pron": pron.get("marcatore") or "—",
                **calc,
            })

        risultato[fase] = {
            "label": FASI_LABEL.get(fase, fase),
            "pt_esito": pt_esito,
            "pt_risultato": pt_ris,
            "pt_marcatore": pt_marc,
            "punti_totali": pt_esito + pt_ris + pt_marc,
            "n_esiti": n_esiti,
            "n_risultati": n_ris,
            "n_marcatori": n_marc,
            "partite": dettaglio,
        }

    return risultato


def punti_eliminatorie_totali(nome_completo: str, eliminatorie: dict) -> int:
    """Somma punti di tutte le fasi eliminatorie per un partecipante."""
    dati = calcola_eliminatorie_partecipante(nome_completo, eliminatorie)
    return sum(f["punti_totali"] for f in dati.values())
