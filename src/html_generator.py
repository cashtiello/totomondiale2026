"""
html_generator.py - Genera la pagina HTML classifica tramite Jinja2.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.models import PunteggioDettaglio
from src.config import OUTPUT_HTML, TEMPLATES_DIR, OUTPUT_DIR
from src.utils import timestamp_ora
from src.logger import get_logger

log = get_logger(__name__)


def _build_records(punteggi: list[PunteggioDettaglio]) -> list[dict]:
    """Costruisce la lista di record/statistiche da mostrare nella pagina."""
    if not punteggi:
        return []

    records = []

    def top(campo: str, etichetta: str, unita: str = "pt") -> dict:
        best = max(punteggi, key=lambda x: getattr(x, campo))
        val  = getattr(best, campo)
        return {"label": etichetta, "nome": best.nome_completo, "valore": f"{val} {unita}"}

    records.append(top("n_risultati_esatti",  "🎯 Record Risultati Esatti",    "risultati"))
    records.append(top("n_marcatori_corretti","👟 Record Marcatori Indovinati", "marcatori"))
    records.append(top("n_esiti_corretti",    "✅ Record Esiti Corretti",       "esiti"))
    records.append(top("pt_gironi",           "🏟️ Record Punti Gironi",         "pt"))
    records.append(top("pt_vincitore",        "🥇 Vincitore Indovinato",        "pt"))
    records.append(top("pt_capocannoniere",   "⚽ Capocannoniere Indovinato",   "pt"))
    records.append(top("pt_assistman",        "🅰️ Assistman Indovinato",        "pt"))
    records.append(top("punti_speciali",      "🌟 Record Punti Speciali",       "pt"))
    records.append(top("punti_partite",       "🔢 Record Punti Partite",        "pt"))

    return records


def genera_html(
    punteggi: list[PunteggioDettaglio],
    n_partite_giocate: int = 0,
    percorso: Path = OUTPUT_HTML,
) -> None:
    """
    Renderizza il template Jinja2 e salva il file HTML.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("classifica.html")

    media = 0.0
    max_punti = 1
    if punteggi:
        media = round(sum(p.punti_totali for p in punteggi) / len(punteggi), 1)
        max_punti = max(p.punti_totali for p in punteggi) or 1

    max_risultati_esatti = max((p.n_risultati_esatti for p in punteggi), default=0)
    max_marcatori        = max((p.n_marcatori_corretti for p in punteggi), default=0)

    html = template.render(
        punteggi=punteggi,
        timestamp=timestamp_ora(),
        n_partecipanti=len(punteggi),
        n_partite_giocate=n_partite_giocate,
        media_punti=media,
        max_punti=max_punti,
        max_risultati_esatti=max_risultati_esatti,
        max_marcatori=max_marcatori,
        records=_build_records(punteggi),
    )

    percorso.write_text(html, encoding="utf-8")
    log.info(f"Pagina HTML salvata: {percorso}")
