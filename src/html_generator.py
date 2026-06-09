"""
html_generator.py - Genera la pagina HTML classifica tramite Jinja2.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.models import PunteggioDettaglio, PronosticoPartecipante, RisultatiReali
from src.config import OUTPUT_HTML, TEMPLATES_DIR, OUTPUT_DIR
from src.utils import timestamp_ora, confronta_squadre, normalizza_risultato
from src.logger import get_logger
from src.calcolo_punti import calcola_statistiche_torneo

log = get_logger(__name__)


def _build_records(punteggi: list[PunteggioDettaglio]) -> list[dict]:
    if not punteggi:
        return []
    records = []
    def top(campo, etichetta, unita="pt"):
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


def _build_dettaglio_partecipante(
    partecipante: PronosticoPartecipante,
    risultati: RisultatiReali,
) -> dict:
    """Costruisce il dettaglio pronostici di un partecipante per il modal."""

    # ── Partite ──────────────────────────────────────────────────────────────
    partite_detail = []
    for pron in partecipante.partite:
        ris_reale = None
        for key, r in risultati.partite.items():
            if confronta_squadre(pron.incontro, key):
                ris_reale = r
                break

        giocata = ris_reale is not None and ris_reale.risultato is not None

        # Esito
        esito_pron = pron.esito
        if not esito_pron and pron.risultato_esatto:
            from src.utils import calcola_esito_da_risultato
            esito_pron = calcola_esito_da_risultato(pron.risultato_esatto)

        esito_ok = False
        risultato_ok = False
        marcatore_ok = False

        if giocata:
            esito_reale = ris_reale.esito
            if esito_pron and esito_reale:
                esito_ok = (esito_pron == esito_reale)

            r_pron = normalizza_risultato(pron.risultato_esatto)
            r_real = normalizza_risultato(ris_reale.risultato)
            if r_pron and r_real:
                risultato_ok = (r_pron == r_real)

            if pron.marcatore and ris_reale.marcatore:
                marcatori_reali = [m.strip() for m in ris_reale.marcatore.split(",") if m.strip()]
                for mr in marcatori_reali:
                    if confronta_squadre(pron.marcatore, mr):
                        marcatore_ok = True
                        break

        partite_detail.append({
            "incontro":        pron.incontro,
            "incontro_display": pron.incontro,
            "esito_pron":      esito_pron or "—",
            "risultato_pron":  pron.risultato_esatto or "—",
            "marcatore_pron":  pron.marcatore or "—",
            "risultato_reale": ris_reale.risultato if giocata else None,
            "marcatore_reale": ris_reale.marcatore if giocata else None,
            "giocata":         giocata,
            "esito_ok":        esito_ok,
            "risultato_ok":    risultato_ok,
            "marcatore_ok":    marcatore_ok,
        })

    # ── Gironi ───────────────────────────────────────────────────────────────
    gironi_detail = []
    for g in partecipante.gironi:
        ris_g = risultati.gironi.get(g.girone)
        definito = ris_g is not None and (ris_g.prima or ris_g.seconda)

        coppia_ok = False
        invertita = False
        singola_prima = False
        singola_seconda = False

        if definito:
            rp = ris_g.prima
            rs = ris_g.seconda
            pp = g.prima
            ps = g.seconda
            if pp and ps and rp and rs:
                if confronta_squadre(pp, rp) and confronta_squadre(ps, rs):
                    coppia_ok = True
                elif confronta_squadre(pp, rs) and confronta_squadre(ps, rp):
                    invertita = True
                else:
                    if rp and (confronta_squadre(pp, rp) or confronta_squadre(ps, rp)):
                        singola_prima = True
                    if rs and (confronta_squadre(pp, rs) or confronta_squadre(ps, rs)):
                        singola_seconda = True

        gironi_detail.append({
            "girone":          g.girone,
            "prima_pron":      g.prima or "—",
            "seconda_pron":    g.seconda or "—",
            "prima_reale":     ris_g.prima if definito else None,
            "seconda_reale":   ris_g.seconda if definito else None,
            "definito":        definito,
            "coppia_ok":       coppia_ok,
            "invertita":       invertita,
            "singola_prima":   singola_prima,
            "singola_seconda": singola_seconda,
        })

    # ── Speciali ─────────────────────────────────────────────────────────────
    s = partecipante.speciali
    r = risultati
    speciali_detail = [
        {
            "voce":    "🏆 Vincitore Mondiale",
            "pron":    s.vincitore or "—",
            "reale":   r.vincitore,
            "ok":      bool(s.vincitore and r.vincitore and confronta_squadre(s.vincitore, r.vincitore)),
        },
        {
            "voce":    "🥇 Finalista 1",
            "pron":    s.finalista_1 or "—",
            "reale":   r.finalista_1,
            "ok":      bool(s.finalista_1 and r.finalista_1 and confronta_squadre(s.finalista_1, r.finalista_1)),
        },
        {
            "voce":    "🥈 Finalista 2",
            "pron":    s.finalista_2 or "—",
            "reale":   r.finalista_2,
            "ok":      bool(s.finalista_2 and r.finalista_2 and confronta_squadre(s.finalista_2, r.finalista_2)),
        },
        {
            "voce":    "⚽ Capocannoniere",
            "pron":    s.capocannoniere or "—",
            "reale":   r.capocannoniere,
            "ok":      bool(s.capocannoniere and r.capocannoniere and confronta_squadre(s.capocannoniere, r.capocannoniere)),
        },
        {
            "voce":    "🅰️ Assistman",
            "pron":    s.assistman or "—",
            "reale":   r.assistman,
            "ok":      bool(s.assistman and r.assistman and confronta_squadre(s.assistman, r.assistman)),
        },
        {
            "voce":    "⭐ MVP Torneo",
            "pron":    s.mvp or "—",
            "reale":   r.mvp,
            "ok":      bool(s.mvp and r.mvp and confronta_squadre(s.mvp, r.mvp)),
        },
        {
            "voce":    "🧤 Miglior Portiere",
            "pron":    s.miglior_portiere or "—",
            "reale":   r.miglior_portiere,
            "ok":      bool(s.miglior_portiere and r.miglior_portiere and confronta_squadre(s.miglior_portiere, r.miglior_portiere)),
        },
        {
            "voce":    "🌟 Miglior Giovane U21",
            "pron":    s.miglior_giovane or "—",
            "reale":   r.miglior_giovane,
            "ok":      bool(s.miglior_giovane and r.miglior_giovane and confronta_squadre(s.miglior_giovane, r.miglior_giovane)),
        },
    ]

    return {
        "nome":     partecipante.nome_completo,
        "partite":  partite_detail,
        "gironi":   gironi_detail,
        "speciali": speciali_detail,
    }


def genera_html(
    punteggi: list[PunteggioDettaglio],
    n_partite_giocate: int = 0,
    percorso: Path = OUTPUT_HTML,
    partecipanti: list[PronosticoPartecipante] = None,
    risultati: RisultatiReali = None,
    storico_path: Path = None,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Leggi storico posizioni precedenti
    storico = {}
    if storico_path and storico_path.exists():
        try:
            import json
            with open(storico_path, encoding="utf-8") as f:
                storico = json.load(f)
        except Exception:
            pass

    # Aggiungi variazione a ogni punteggio
    for idx, p in enumerate(punteggi):
        pos_attuale = idx + 1
        pos_precedente = storico.get(p.nome_completo)
        if pos_precedente is None:
            p.variazione = "new"
        elif pos_precedente > pos_attuale:
            p.variazione = "su"
        elif pos_precedente < pos_attuale:
            p.variazione = "giu"
        else:
            p.variazione = "stabile"

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

    # Costruisci dettagli per ogni partecipante
    dettagli = {}
    if partecipanti and risultati:
        for p in partecipanti:
            dettagli[p.nome_completo] = _build_dettaglio_partecipante(p, risultati)

    # Calcola statistiche torneo
    stats = {}
    if partecipanti and risultati and punteggi:
        from src.calcolo_punti import calcola_statistiche_torneo
        stats = calcola_statistiche_torneo(partecipanti, risultati, punteggi)

    html = template.render(
        punteggi=punteggi,
        timestamp=timestamp_ora(),
        n_partecipanti=len(punteggi),
        n_partite_giocate=n_partite_giocate,
        media_punti=media,
        max_punti=max_punti,
        max_risultati_esatti=max((p.n_risultati_esatti for p in punteggi), default=0),
        max_marcatori=max((p.n_marcatori_corretti for p in punteggi), default=0),
        records=_build_records(punteggi),
        dettagli=dettagli,
        stats=stats,
    )

    percorso.write_text(html, encoding="utf-8")
    log.info(f"Pagina HTML salvata: {percorso}")
