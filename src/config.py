"""
config.py - Configurazione centralizzata del progetto Totomondiale 2026
"""
from pathlib import Path


# ── Percorsi ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent

DATA_DIR          = BASE_DIR / "data"
PRONOSTICI_DIR    = DATA_DIR / "pronostici"
RISULTATI_DIR     = DATA_DIR / "risultati_reali"
OUTPUT_DIR        = DATA_DIR / "output"
LOGS_DIR          = DATA_DIR / "logs"
TEMPLATES_DIR     = BASE_DIR / "templates"

RISULTATI_FILE    = RISULTATI_DIR / "risultati.xlsx"
OUTPUT_CLASSIFICA = OUTPUT_DIR / "classifica.xlsx"
OUTPUT_HTML       = OUTPUT_DIR / "index.html"

# ── Punteggi ─────────────────────────────────────────────────────────────────
PUNTI_ESITO             = 1
PUNTI_RISULTATO_ESATTO  = 5
PUNTI_MARCATORE         = 2

PUNTI_COPPIA_GIRONE_ESATTA    = 6
PUNTI_COPPIA_GIRONE_INVERTITA = 4
PUNTI_SINGOLA_QUALIFICATA     = 1   # per ogni singola squadra qualificata indovinata

PUNTI_FINALE_ESATTA     = 15   # entrambe le finaliste corrette
PUNTI_FINALISTA_SINGOLA = 10   # una sola finalista corretta
PUNTI_VINCITORE         = 20
PUNTI_CAPOCANNONIERE    = 10
PUNTI_ASSISTMAN         = 12
PUNTI_MVP               = 10
PUNTI_MIGLIOR_PORTIERE  = 10
PUNTI_MIGLIOR_GIOVANE   = 15

# ── Struttura foglio TABELLONE ────────────────────────────────────────────────
# Righe (0-indexed dal foglio Excel, riga 1 = index 0)
ROW_NOME      = 0   # "NOME"    -> C1
ROW_COGNOME   = 1   # "COGNOME" -> C2
ROW_HEADER    = 4   # intestazioni colonne (DATA, GRUPPO, INCONTRO, ...)
ROW_INIZIO_PARTITE = 5   # prima partita

# Colonne (0-indexed)
COL_DATA      = 0   # A
COL_GRUPPO    = 1   # B
COL_INCONTRO  = 2   # C
COL_ESITO     = 5   # F
COL_RISULTATO = 6   # G
COL_MARCATORE = 7   # H

# Colonne gironi (sulla destra)
COL_GIRONE_NOME  = 9   # J  - nome girone (A, B, ...)
COL_GIRONE_PRIMA = 11  # L  - 1° classificata
COL_GIRONE_SECON = 14  # O  - 2° classificata

# Colonne speciali (sulla destra, righe specifiche)
COL_SPECIALE_LABEL = 11  # L - label del pronostico speciale
COL_SPECIALE_VAL1  = 12  # M - valore 1
COL_SPECIALE_VAL2  = 15  # P - valore 2 (per finale)

# Encoding
ENCODING = "utf-8"

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE   = LOGS_DIR / "totomondiale.log"
LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE   = "%Y-%m-%d %H:%M:%S"

# ── Gironi del Mondiale 2026 ─────────────────────────────────────────────────
GIRONI = list("ABCDEFGHIJKL")   # 12 gironi

# Gruppi di partite: le righe vuote (senza data) separano sezioni speciali
RIGA_MAX_PARTITE = 82   # limite massimo righe da leggere nel tabellone
