"""
main.py - Entry point del Totomondiale 2026 Manager.

Avvio:
    python main.py

Flusso:
    1. Setup logging e cartelle
    2. Leggi tutti i file pronostici da data/pronostici/
    3. Leggi risultati reali da data/risultati_reali/risultati.xlsx
    4. Calcola punteggi per ogni partecipante
    5. Genera classifica Excel → data/output/classifica.xlsx
    6. Genera pagina HTML    → data/output/index.html
    7. Mostra riepilogo a video
"""

import sys
import os
import time
from pathlib import Path

# Aggiungi la root del progetto al path (necessario per import assoluti)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger
from src.config import (
    PRONOSTICI_DIR, RISULTATI_FILE, OUTPUT_CLASSIFICA, OUTPUT_HTML,
    OUTPUT_DIR, LOGS_DIR
)
from src.excel_reader import leggi_tutti_pronostici
from src.parser_risultati import leggi_risultati
from src.calcolo_punti import calcola_tutti_punteggi
from src.generatore_classifica import genera_excel_classifica
from src.html_generator import genera_html


def _crea_struttura_cartelle() -> None:
    """Assicura che tutte le cartelle necessarie esistano."""
    for d in (PRONOSTICI_DIR, RISULTATI_FILE.parent, OUTPUT_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _stampa_banner() -> None:
    print()
    print("=" * 60)
    print("   🏆  TOTOMONDIALE 2026 – MANAGER AUTOMATICO  🏆")
    print("=" * 60)
    print()


def _stampa_riepilogo(punteggi, t_elapsed: float) -> None:
    """Mostra a video un riepilogo rapido della classifica."""
    print()
    print("=" * 60)
    print("  CLASSIFICA FINALE")
    print("=" * 60)
    medaglie = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(punteggi[:10]):  # Top 10
        medaglia = medaglie[i] if i < 3 else "  "
        print(f"  {medaglia} {i+1:>2}. {p.nome_completo:<28} {p.punti_totali:>5} pt")
    if len(punteggi) > 10:
        print(f"      ... e altri {len(punteggi) - 10} partecipanti")
    print()
    print(f"  📄 Excel : {OUTPUT_CLASSIFICA}")
    print(f"  🌐 HTML  : {OUTPUT_HTML}")
    print()
    print(f"  ✅ Completato in {t_elapsed:.2f}s")
    print("=" * 60)
    print()


def main() -> int:
    """
    Funzione principale. Ritorna 0 in caso di successo, 1 in caso di errore.
    """
    t_start = time.perf_counter()

    _stampa_banner()
    _crea_struttura_cartelle()
    setup_logging()
    log = get_logger("main")

    log.info("▶ Avvio TotoMondiale 2026 Manager")

    # ── 1. Leggi pronostici ──────────────────────────────────────────────────
    print("📂 Lettura file pronostici...")
    partecipanti = leggi_tutti_pronostici(PRONOSTICI_DIR)

    if not partecipanti:
        log.warning("⚠️  Nessun partecipante caricato.")
        print()
        print("  ⚠️  Nessun file trovato in:", PRONOSTICI_DIR)
        print("  👉  Copia i file .xlsx dei partecipanti nella cartella")
        print(f"      {PRONOSTICI_DIR}")
        print()
        # Crea comunque il file risultati di esempio e un HTML vuoto
        print("📋 Creo file risultati di esempio...")
        leggi_risultati(RISULTATI_FILE)
        genera_html([], percorso=OUTPUT_HTML)
        genera_excel_classifica([], percorso=OUTPUT_CLASSIFICA)
        print(f"  ✅ File di esempio creati in {OUTPUT_DIR}")
        return 0

    print(f"  ✅ {len(partecipanti)} partecipanti caricati")

    # ── 2. Leggi risultati reali ─────────────────────────────────────────────
    print("📋 Lettura risultati reali...")
    risultati = leggi_risultati(RISULTATI_FILE)

    n_partite_reali  = len(risultati.partite)
    n_gironi_reali   = len(risultati.gironi)
    print(f"  ✅ {n_partite_reali} partite | {n_gironi_reali} gironi caricati")

    # ── 3. Calcola punteggi ──────────────────────────────────────────────────
    print("🔢 Calcolo punteggi...")
    punteggi = calcola_tutti_punteggi(partecipanti, risultati)
    print(f"  ✅ Punteggi calcolati per {len(punteggi)} partecipanti")

    # ── 4. Genera Excel ──────────────────────────────────────────────────────
    print("📊 Generazione classifica Excel...")
    genera_excel_classifica(punteggi, percorso=OUTPUT_CLASSIFICA)
    print(f"  ✅ {OUTPUT_CLASSIFICA}")

    # ── 5. Genera HTML ───────────────────────────────────────────────────────
    print("🌐 Generazione pagina HTML...")
    genera_html(
        punteggi,
        n_partite_giocate=n_partite_reali,
        percorso=OUTPUT_HTML,
        partecipanti=partecipanti,
        risultati=risultati,
    )
    print(f"  ✅ {OUTPUT_HTML}")

    # ── Riepilogo ────────────────────────────────────────────────────────────
    t_elapsed = time.perf_counter() - t_start
    log.info(f"✅ Completato in {t_elapsed:.2f}s")
    _stampa_riepilogo(punteggi, t_elapsed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
