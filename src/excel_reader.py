"""
excel_reader.py - Legge tutti i file .xlsx dalla cartella pronostici.
"""
from pathlib import Path
from typing import Optional

from src.models import PronosticoPartecipante
from src.parser_pronostici import parse_file_partecipante
from src.config import PRONOSTICI_DIR
from src.logger import get_logger

log = get_logger(__name__)


def leggi_tutti_pronostici(
    cartella: Path = PRONOSTICI_DIR,
) -> list[PronosticoPartecipante]:
    """
    Scansiona la cartella e legge tutti i file .xlsx trovati.
    I file corrotti o con errori vengono saltati (con log).
    Ritorna la lista dei partecipanti letti con successo.
    """
    cartella.mkdir(parents=True, exist_ok=True)

    file_xlsx = sorted(cartella.glob("*.xlsx"))
    if not file_xlsx:
        log.warning(f"Nessun file .xlsx trovato in {cartella}")
        return []

    log.info(f"Trovati {len(file_xlsx)} file pronostici in {cartella}")

    partecipanti: list[PronosticoPartecipante] = []
    errori = 0

    for file in file_xlsx:
        # Salta file temporanei di Excel (~$nome)
        if file.name.startswith("~$"):
            log.debug(f"Saltato file temporaneo: {file.name}")
            continue

        log.debug(f"Parsing: {file.name}")
        partecipante = parse_file_partecipante(file)

        if partecipante is None:
            errori += 1
            log.error(f"File ignorato per errori: {file.name}")
        else:
            partecipanti.append(partecipante)

    log.info(
        f"Caricati {len(partecipanti)} partecipanti | {errori} file con errori"
    )
    return partecipanti
