"""
calcolo_punti.py - Logica di calcolo punteggi per il Totomondiale 2026.

Regolamento implementato:

PARTITE
  Esito 1X2 corretto            → 1 pt
  Risultato esatto corretto     → 5 pt  (+ 1 pt esito automatico)
  Marcatore corretto            → 2 pt

GIRONI
  Accoppiata esatta (ordine corretto) → 6 pt
  Accoppiata giusta (ordine errato)   → 4 pt
  Singola squadra qualificata         → 1 pt per squadra indovinata

SEZIONI SPECIALI
  Finale esatta (entrambe)      → 15 pt
  Finalista singola             → 10 pt per finalista indovinata
  Vincitore competizione        → 20 pt
  Capocannoniere                → 10 pt
  Assistman                     → 12 pt
  MVP Torneo                    → 10 pt
  Miglior Portiere              → 10 pt
  Miglior Giovane U21           → 15 pt
"""

from src.models import (
    PronosticoPartecipante, RisultatiReali, PunteggioDettaglio
)
from src.utils import (
    confronta_squadre, normalizza_risultato,
    normalizza_esito, calcola_esito_da_risultato
)
from src.config import (
    PUNTI_ESITO, PUNTI_RISULTATO_ESATTO, PUNTI_MARCATORE,
    PUNTI_COPPIA_GIRONE_ESATTA, PUNTI_COPPIA_GIRONE_INVERTITA,
    PUNTI_SINGOLA_QUALIFICATA,
    PUNTI_FINALE_ESATTA, PUNTI_FINALISTA_SINGOLA,
    PUNTI_VINCITORE, PUNTI_CAPOCANNONIERE, PUNTI_ASSISTMAN,
    PUNTI_MVP, PUNTI_MIGLIOR_PORTIERE, PUNTI_MIGLIOR_GIOVANE,
)
from src.logger import get_logger

log = get_logger(__name__)


def _calcola_partite(
    partecipante: PronosticoPartecipante,
    risultati: RisultatiReali,
    dettaglio: PunteggioDettaglio,
) -> None:
    """Calcola i punti per tutte le partite del tabellone."""

    for pron in partecipante.partite:
        incontro_key = pron.incontro
        # Cerca il risultato reale corrispondente (confronto case-insensitive)
        risultato_reale = None
        for key, ris in risultati.partite.items():
            if confronta_squadre(incontro_key, key):
                risultato_reale = ris
                break

        if risultato_reale is None:
            # Partita non ancora giocata o non presente nei risultati
            continue

        esito_reale = risultato_reale.esito

        # ── Risultato esatto ─────────────────────────────────────────────────
        if pron.risultato_esatto and risultato_reale.risultato:
            r_pron = normalizza_risultato(pron.risultato_esatto)
            r_real = normalizza_risultato(risultato_reale.risultato)
            if r_pron and r_real and r_pron == r_real:
                dettaglio.pt_risultato_esatto += PUNTI_RISULTATO_ESATTO
                dettaglio.n_risultati_esatti += 1
                # Il risultato esatto include automaticamente l'esito
                dettaglio.pt_esito += PUNTI_ESITO
                dettaglio.n_esiti_corretti += 1
                log.debug(
                    f"{dettaglio.nome_completo} | {incontro_key}: "
                    f"risultato esatto {r_pron} +{PUNTI_RISULTATO_ESATTO + PUNTI_ESITO}pt"
                )
            else:
                # ── Solo esito ───────────────────────────────────────────────
                esito_pron = pron.esito or calcola_esito_da_risultato(pron.risultato_esatto)
                if esito_pron and esito_reale and esito_pron == esito_reale:
                    dettaglio.pt_esito += PUNTI_ESITO
                    dettaglio.n_esiti_corretti += 1
                    log.debug(
                        f"{dettaglio.nome_completo} | {incontro_key}: "
                        f"esito {esito_pron} +{PUNTI_ESITO}pt"
                    )
        else:
            # Nessun risultato esatto, guarda solo esito
            esito_pron = pron.esito or calcola_esito_da_risultato(pron.risultato_esatto)
            if esito_pron and esito_reale and esito_pron == esito_reale:
                dettaglio.pt_esito += PUNTI_ESITO
                dettaglio.n_esiti_corretti += 1
                log.debug(
                    f"{dettaglio.nome_completo} | {incontro_key}: "
                    f"esito {esito_pron} +{PUNTI_ESITO}pt"
                )

        # ── Marcatore ────────────────────────────────────────────────────────
        if pron.marcatore and risultato_reale.marcatore:
            # Supporta più marcatori separati da virgola nel file risultati
            # es. "Kane, Foden, Mbappe"
            marcatori_reali = [
                m.strip() for m in risultato_reale.marcatore.split(",")
                if m.strip()
            ]
            for marcatore_reale in marcatori_reali:
                if confronta_squadre(pron.marcatore, marcatore_reale):
                    dettaglio.pt_marcatore += PUNTI_MARCATORE
                    dettaglio.n_marcatori_corretti += 1
                    log.debug(
                        f"{dettaglio.nome_completo} | {incontro_key}: "
                        f"marcatore {pron.marcatore} +{PUNTI_MARCATORE}pt"
                    )
                    break  # basta trovarne uno, non sommare doppio


def _calcola_gironi(
    partecipante: PronosticoPartecipante,
    risultati: RisultatiReali,
    dettaglio: PunteggioDettaglio,
) -> None:
    """Calcola i punti per le accoppiata girone."""

    for pron in partecipante.gironi:
        girone = pron.girone
        risultato_girone = risultati.gironi.get(girone)

        if risultato_girone is None:
            continue  # Girone non ancora concluso

        r_prima = risultato_girone.prima
        r_secon = risultato_girone.seconda
        p_prima = pron.prima
        p_secon = pron.seconda

        # ── Accoppiata esatta (ordine corretto) ──────────────────────────────
        if (p_prima and p_secon and r_prima and r_secon
                and confronta_squadre(p_prima, r_prima)
                and confronta_squadre(p_secon, r_secon)):
            dettaglio.pt_gironi += PUNTI_COPPIA_GIRONE_ESATTA
            dettaglio.n_gironi_coppia_esatta += 1
            log.debug(
                f"{dettaglio.nome_completo} | Girone {girone}: "
                f"coppia esatta +{PUNTI_COPPIA_GIRONE_ESATTA}pt"
            )
            continue

        # ── Accoppiata invertita ─────────────────────────────────────────────
        if (p_prima and p_secon and r_prima and r_secon
                and confronta_squadre(p_prima, r_secon)
                and confronta_squadre(p_secon, r_prima)):
            dettaglio.pt_gironi += PUNTI_COPPIA_GIRONE_INVERTITA
            dettaglio.n_gironi_coppia_invertita += 1
            log.debug(
                f"{dettaglio.nome_completo} | Girone {girone}: "
                f"coppia invertita +{PUNTI_COPPIA_GIRONE_INVERTITA}pt"
            )
            continue

        # ── Singole squadre qualificate ──────────────────────────────────────
        qualificate_reali = {r_prima, r_secon} - {None}
        pronosticate = {p_prima, p_secon} - {None}

        for pq in pronosticate:
            for qr in qualificate_reali:
                if confronta_squadre(pq, qr):
                    dettaglio.pt_gironi += PUNTI_SINGOLA_QUALIFICATA
                    dettaglio.n_gironi_singola += 1
                    log.debug(
                        f"{dettaglio.nome_completo} | Girone {girone}: "
                        f"singola {pq} +{PUNTI_SINGOLA_QUALIFICATA}pt"
                    )
                    break


def _calcola_speciali(
    partecipante: PronosticoPartecipante,
    risultati: RisultatiReali,
    dettaglio: PunteggioDettaglio,
) -> None:
    """Calcola i punti per i pronostici speciali."""
    s = partecipante.speciali
    r = risultati

    # ── Vincitore competizione ───────────────────────────────────────────────
    if s.vincitore and r.vincitore:
        if confronta_squadre(s.vincitore, r.vincitore):
            dettaglio.pt_vincitore += PUNTI_VINCITORE
            log.debug(f"{dettaglio.nome_completo}: vincitore +{PUNTI_VINCITORE}pt")

    # ── Finalista/Finale ────────────────────────────────────────────────────
    finalisti_reali = set()
    if r.finalista_1:
        finalisti_reali.add(r.finalista_1)
    if r.finalista_2:
        finalisti_reali.add(r.finalista_2)

    finalisti_pron = set()
    if s.finalista_1:
        finalisti_pron.add(s.finalista_1)
    if s.finalista_2:
        finalisti_pron.add(s.finalista_2)

    # Conta quante finaliste indovinate (normalizzato)
    indovinate = 0
    for fp in finalisti_pron:
        for fr in finalisti_reali:
            if confronta_squadre(fp, fr):
                indovinate += 1
                break

    if indovinate == 2 and len(finalisti_reali) == 2:
        # Finale esatta (entrambe le squadre, indipendente dall'ordine)
        # Ma se l'ordine è esatto vale di più?
        # Regolamento: "Finale esatta: 15 pt" → interpretato come entrambe le finaliste corrette
        dettaglio.pt_finalista += PUNTI_FINALE_ESATTA
        log.debug(f"{dettaglio.nome_completo}: finale esatta +{PUNTI_FINALE_ESATTA}pt")
    elif indovinate == 1:
        dettaglio.pt_finalista += PUNTI_FINALISTA_SINGOLA
        log.debug(f"{dettaglio.nome_completo}: finalista singola +{PUNTI_FINALISTA_SINGOLA}pt")

    # ── Premi individuali ────────────────────────────────────────────────────
    premi = [
        (s.capocannoniere,   r.capocannoniere,   PUNTI_CAPOCANNONIERE,   "pt_capocannoniere"),
        (s.assistman,        r.assistman,         PUNTI_ASSISTMAN,        "pt_assistman"),
        (s.mvp,              r.mvp,               PUNTI_MVP,              "pt_mvp"),
        (s.miglior_portiere, r.miglior_portiere,  PUNTI_MIGLIOR_PORTIERE, "pt_miglior_portiere"),
        (s.miglior_giovane,  r.miglior_giovane,   PUNTI_MIGLIOR_GIOVANE,  "pt_miglior_giovane"),
    ]

    for val_pron, val_reale, punti, campo in premi:
        if val_pron and val_reale and confronta_squadre(val_pron, val_reale):
            setattr(dettaglio, campo, getattr(dettaglio, campo) + punti)
            log.debug(f"{dettaglio.nome_completo}: {campo} +{punti}pt")


def calcola_punteggio(
    partecipante: PronosticoPartecipante,
    risultati: RisultatiReali,
) -> PunteggioDettaglio:
    """
    Calcola il punteggio completo di un partecipante.
    Restituisce un PunteggioDettaglio con tutti i breakdown.
    """
    dettaglio = PunteggioDettaglio(
        nome_completo=partecipante.nome_completo,
        nome=partecipante.nome,
        cognome=partecipante.cognome,
        file_sorgente=partecipante.file_sorgente,
    )

    _calcola_partite(partecipante, risultati, dettaglio)
    _calcola_gironi(partecipante, risultati, dettaglio)
    _calcola_speciali(partecipante, risultati, dettaglio)

    log.info(
        f"Punteggio {dettaglio.nome_completo}: "
        f"TOT={dettaglio.punti_totali} "
        f"(partite={dettaglio.punti_partite}, "
        f"gironi={dettaglio.pt_gironi}, "
        f"speciali={dettaglio.punti_speciali})"
    )
    return dettaglio


def calcola_statistiche_torneo(
    partecipanti: list[PronosticoPartecipante],
    risultati: RisultatiReali,
    punteggi: list[PunteggioDettaglio],
) -> dict:
    """Calcola statistiche aggregate del torneo per la sezione stats nell'HTML."""
    n = len(partecipanti)
    if n == 0:
        return {}

    # ── Statistiche per partita ───────────────────────────────────────────
    stats_partite = {}
    for incontro, ris in risultati.partite.items():
        if not ris.risultato:
            continue
        n_esito = n_ris = n_marc = 0
        for part in partecipanti:
            for pron in part.partite:
                if not confronta_squadre(pron.incontro, incontro):
                    continue
                esito_pron = pron.esito or calcola_esito_da_risultato(pron.risultato_esatto)
                if esito_pron and ris.esito and esito_pron == ris.esito:
                    n_esito += 1
                r_p = normalizza_risultato(pron.risultato_esatto)
                r_r = normalizza_risultato(ris.risultato)
                if r_p and r_r and r_p == r_r:
                    n_ris += 1
                if pron.marcatore and ris.marcatore:
                    for mr in [m.strip() for m in ris.marcatore.split(",") if m.strip()]:
                        if confronta_squadre(pron.marcatore, mr):
                            n_marc += 1
                            break
        stats_partite[incontro] = {
            "risultato": ris.risultato,
            "n_esito": n_esito,
            "n_risultato": n_ris,
            "n_marcatore": n_marc,
            "pct_esito": round(n_esito / n * 100),
        }

    # ── Partita più/meno indovinata ───────────────────────────────────────
    giocate = {k: v for k, v in stats_partite.items() if v["n_esito"] > 0 or v["n_risultato"] > 0}
    partita_piu_indovinata = max(giocate, key=lambda k: giocate[k]["pct_esito"]) if giocate else None
    partita_meno_indovinata = min(giocate, key=lambda k: giocate[k]["pct_esito"]) if giocate else None

    # ── Pronostico vincitore più gettonato ────────────────────────────────
    voti_vincitore = {}
    for part in partecipanti:
        v = part.speciali.vincitore
        if v:
            voti_vincitore[v] = voti_vincitore.get(v, 0) + 1
    vincitore_gettonato = sorted(voti_vincitore.items(), key=lambda x: x[1], reverse=True)[:5]

    # ── Totali aggregati ──────────────────────────────────────────────────
    tot_esiti    = sum(p.n_esiti_corretti for p in punteggi)
    tot_risultati = sum(p.n_risultati_esatti for p in punteggi)
    tot_marcatori = sum(p.n_marcatori_corretti for p in punteggi)
    tot_gironi_esatti = sum(p.n_gironi_coppia_esatta for p in punteggi)

    # ── Chi ha fatto meglio nelle partite vs gironi vs speciali ──────────
    top_partite  = max(punteggi, key=lambda p: p.punti_partite)
    top_gironi   = max(punteggi, key=lambda p: p.pt_gironi)
    top_speciali = max(punteggi, key=lambda p: p.punti_speciali)
    top_esiti    = max(punteggi, key=lambda p: p.n_esiti_corretti)
    top_marcatori = max(punteggi, key=lambda p: p.n_marcatori_corretti)

    # ── Marcatore più indovinato ──────────────────────────────────────────
    marc_counts = {}
    for part in partecipanti:
        for pron in part.partite:
            if not pron.marcatore:
                continue
            for incontro, ris in risultati.partite.items():
                if not confronta_squadre(pron.incontro, incontro) or not ris.marcatore:
                    continue
                for mr in [m.strip() for m in ris.marcatore.split(",") if m.strip()]:
                    if confronta_squadre(pron.marcatore, mr):
                        marc_counts[mr] = marc_counts.get(mr, 0) + 1
    marcatore_top = max(marc_counts.items(), key=lambda x: x[1]) if marc_counts else None

    # ── Distribuzione punteggi ────────────────────────────────────────────
    fasce = {"0-20": 0, "21-30": 0, "31-40": 0, "41+": 0}
    for p in punteggi:
        t = p.punti_totali
        if t <= 20:      fasce["0-20"] += 1
        elif t <= 30:    fasce["21-30"] += 1
        elif t <= 40:    fasce["31-40"] += 1
        else:            fasce["41+"] += 1

    return {
        "n_partecipanti":         n,
        "tot_esiti":              tot_esiti,
        "tot_risultati":          tot_risultati,
        "tot_marcatori":          tot_marcatori,
        "tot_gironi_esatti":      tot_gironi_esatti,
        "media_esiti":            round(tot_esiti / n, 1),
        "media_risultati":        round(tot_risultati / n, 1),
        "media_marcatori":        round(tot_marcatori / n, 1),
        "top_partite":            {"nome": top_partite.nome_completo,  "val": top_partite.punti_partite},
        "top_gironi":             {"nome": top_gironi.nome_completo,   "val": top_gironi.pt_gironi},
        "top_speciali":           {"nome": top_speciali.nome_completo, "val": top_speciali.punti_speciali},
        "top_esiti":              {"nome": top_esiti.nome_completo,    "val": top_esiti.n_esiti_corretti},
        "top_marcatori":          {"nome": top_marcatori.nome_completo,"val": top_marcatori.n_marcatori_corretti},
        "partita_piu_indovinata": {"nome": partita_piu_indovinata, **giocate[partita_piu_indovinata]} if partita_piu_indovinata else None,
        "partita_meno_indovinata":{"nome": partita_meno_indovinata, **giocate[partita_meno_indovinata]} if partita_meno_indovinata else None,
        "marcatore_top":          {"nome": marcatore_top[0], "val": marcatore_top[1]} if marcatore_top else None,
        "vincitore_gettonato":    vincitore_gettonato,
        "stats_partite":          stats_partite,
        "fasce":                  fasce,
    }


def calcola_tutti_punteggi(
    partecipanti: list[PronosticoPartecipante],
    risultati: RisultatiReali,
) -> list[PunteggioDettaglio]:
    """
    Calcola i punteggi per tutti i partecipanti e restituisce la lista ordinata.

    Criteri di ordinamento (in caso di parità):
      1. Punti totali (desc)
      2. Numero risultati esatti indovinati (desc)
      3. Numero marcatori indovinati (desc)
    """
    punteggi = [calcola_punteggio(p, risultati) for p in partecipanti]
    punteggi.sort(
        key=lambda x: (
            x.punti_totali,
            x.n_risultati_esatti,
            x.n_marcatori_corretti,
        ),
        reverse=True,
    )
    return punteggi