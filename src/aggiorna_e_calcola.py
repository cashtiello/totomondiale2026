"""
aggiorna_e_calcola.py
Script eseguito da GitHub Actions ogni ora.

1. Legge API_FOOTBALL_KEY dalla variabile d'ambiente (GitHub Secret)
2. Scarica risultati reali da API-Football
3. Aggiorna risultati.xlsx
4. Calcola classifica
5. Genera index.html
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger
from src.config import RISULTATI_FILE
from src.excel_reader import leggi_tutti_pronostici
from src.parser_risultati import leggi_risultati
from src.calcolo_punti import calcola_tutti_punteggi
from src.generatore_classifica import genera_excel_classifica
from src.html_generator import genera_html

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

setup_logging()
log = get_logger("aggiorna_e_calcola")

# ── Configurazione ────────────────────────────────────────────────────────────
API_KEY      = os.environ.get("FOOTBALL_DATA_KEY", "")
API_BASE     = "https://api.football-data.org/v4"
CODICE_WC    = "WC"  # FIFA World Cup su football-data.org

# Gironi per i dropdown
GIRONI_SQUADRE = {
    'A': ['Messico', 'Sud Africa', 'Corea del Sud', 'Repubblica Ceca'],
    'B': ['Canada', 'Bosnia Erzegovina', 'Qatar', 'Svizzera'],
    'C': ['Brasile', 'Marocco', 'Haiti', 'Scozia'],
    'D': ['USA', 'Paraguay', 'Australia', 'Turchia'],
    'E': ['Germania', 'Curacao', "Costa d'Avorio", 'Ecuador'],
    'F': ['Olanda', 'Giappone', 'Svezia', 'Tunisia'],
    'G': ['Belgio', 'Egitto', 'Iran', 'Nuova Zelanda'],
    'H': ['Spagna', 'Capo Verde', 'Arabia Saudita', 'Uruguay'],
    'I': ['Francia', 'Senegal', 'Iraq', 'Norvegia'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Giordania'],
    'K': ['Portogallo', 'Congo', 'Uzbekistan', 'Colombia'],
    'L': ['Inghilterra', 'Croazia', 'Ghana', 'Panama'],
}

TUTTE_LE_PARTITE = [
    ("Messico-Sud Africa","A"), ("Corea del Sud-R.Ceca","A"),
    ("Canada-Bosnia","B"), ("USA-Paraguay","D"), ("Qatar-Svizzera","B"),
    ("Brasile-Marocco","C"), ("Haiti-Scozia","C"), ("Australia-Turchia","D"),
    ("Germania-Curacao","E"), ("Olanda-Giappone","F"),
    ("Costa d'Avorio-Ecuador","E"), ("Svezia-Tunisia","F"),
    ("Spagna-Capo Verde","H"), ("Belgio-Egitto","G"),
    ("Arabia Saudita-Uruguay","H"), ("Iran-Nuova Zelanda","G"),
    ("Francia-Senegal","I"), ("Iraq-Norvegia","I"),
    ("Argentina-Algeria","J"), ("Austria-Giordania","J"),
    ("Portogallo-Congo","K"), ("Inghilterra-Croazia","L"),
    ("Ghana-Panama","L"), ("Uzbekistan-Colombia","K"),
    ("R.Ceca-Sud Africa","A"), ("Svizzera-Bosnia","B"),
    ("Canada-Qatar","B"), ("Messico-Corea del Sud","A"),
    ("USA-Australia","D"), ("Scozia-Marocco","C"),
    ("Brasile-Haiti","C"), ("Turchia-Paraguay","D"),
    ("Olanda-Svezia","F"), ("Germania-Costa d'Avorio","E"),
    ("Ecuador-Curacao","E"), ("Tunisia-Giappone","F"),
    ("Spagna-Arabia Saudita","H"), ("Belgio-Iran","G"),
    ("Uruguay-Capo Verde","H"), ("Nuova Zelanda-Egitto","G"),
    ("Argentina-Austria","J"), ("Francia-Iraq","I"),
    ("Norvegia-Senegal","I"), ("Giordania-Algeria","J"),
    ("Portogallo-Uzbekistan","K"), ("Inghilterra-Ghana","L"),
    ("Panama-Croazia","L"), ("Colombia-Congo","K"),
    ("Svizzera-Canada","B"), ("Bosnia-Qatar","B"),
    ("Scozia-Brasile","C"), ("Marocco-Haiti","C"),
    ("R.Ceca-Messico","A"), ("Sud Africa-Corea del Sud","A"),
    ("Ecuador-Germania","E"), ("Curacao-Costa d'Avorio","E"),
    ("Tunisia-Olanda","F"), ("Giappone-Svezia","F"),
    ("Paraguay-Australia","D"), ("Turchia-USA","D"),
    ("Norvegia-Francia","I"), ("Senegal-Iraq","I"),
    ("Uruguay-Spagna","H"), ("Capo Verde-Arabia Saudita","H"),
    ("Egitto-Iran","G"), ("Nuova Zelanda-Belgio","G"),
    ("Panama-Inghilterra","L"), ("Croazia-Ghana","L"),
    ("Colombia-Portogallo","K"), ("Congo-Uzbekistan","K"),
    ("Giordania-Argentina","J"), ("Algeria-Austria","J"),
]


def _api(endpoint: str) -> dict:
    """Chiama football-data.org e ritorna il JSON."""
    url = f"{API_BASE}/{endpoint}"
    req = urllib.request.Request(url, headers={"X-Auth-Token": API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log.error(f"Errore API {endpoint}: {e}")
        return {}


def scarica_risultati() -> dict[str, dict]:
    """Scarica risultati e marcatori di tutte le partite finite."""
    log.info("Scarico partite da football-data.org...")
    data = _api(f"competitions/{CODICE_WC}/matches?status=FINISHED")
    risultati = {}

    for match in data.get("matches", []):
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        gh   = match["score"]["fullTime"]["home"] or 0
        ga   = match["score"]["fullTime"]["away"] or 0
        mid  = match["id"]
        nome = f"{home}-{away}"

        # Scarica marcatori tramite endpoint dettaglio partita
        time.sleep(0.3)
        det = _api(f"matches/{mid}")
        gol = []
        ha_autogol = False
        for goal in det.get("goals", []):
            if goal.get("type") == "OWN":
                ha_autogol = True
            else:
                scorer = goal.get("scorer", {}).get("name", "")
                if scorer and scorer not in gol:
                    gol.append(scorer)

        marcatori_str = ", ".join(gol)
        if ha_autogol:
            marcatori_str = (marcatori_str + ", autogol").strip(", ")

        risultati[nome] = {
            "risultato": f"{gh}-{ga}",
            "marcatori": marcatori_str,
        }
        log.info(f"  {nome}: {gh}-{ga} | {marcatori_str}")

    log.info(f"Scaricate {len(risultati)} partite completate")
    return risultati


def scarica_gironi() -> dict[str, dict]:
    """Scarica le classifiche dei gironi."""
    log.info("Scarico classifiche gironi...")
    data = _api(f"competitions/{CODICE_WC}/standings")
    classifiche = {}

    for standing in data.get("standings", []):
        if standing.get("type") != "TOTAL":
            continue
        gruppo = standing.get("group", "")
        # es. "GROUP_A" → "A"
        lettera = gruppo.replace("GROUP_", "").strip()
        tabella = standing.get("table", [])
        if len(tabella) >= 2:
            classifiche[lettera] = {
                "prima":   tabella[0]["team"]["name"],
                "seconda": tabella[1]["team"]["name"],
            }

    log.info(f"Classifiche gironi: {len(classifiche)}")
    return classifiche


def scrivi_risultati(partite: dict, gironi: dict) -> None:
    """Scrive risultati.xlsx con i dati aggiornati."""
    bordo = lambda: Border(
        left=Side(style='thin', color='BDC3C7'),
        right=Side(style='thin', color='BDC3C7'),
        top=Side(style='thin', color='BDC3C7'),
        bottom=Side(style='thin', color='BDC3C7'),
    )
    h_fill = PatternFill("solid", start_color="2E4057")
    h_font = Font(bold=True, color="FFFFFF", size=11)
    h_alg  = Alignment(horizontal="center", vertical="center")
    f_alt  = [PatternFill("solid", start_color="F8F9FA"),
              PatternFill("solid", start_color="FFFFFF")]

    wb = openpyxl.Workbook()

    # ── PARTITE ───────────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = "PARTITE"
    for col, h in enumerate(["PARTITA", "RISULTATO", "MARCATORE"], 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = h_font; c.fill = h_fill
        c.alignment = h_alg; c.border = bordo()
    ws.row_dimensions[1].height = 24

    for i, (incontro, _) in enumerate(TUTTE_LE_PARTITE):
        info = partite.get(incontro, {})
        for col, val in enumerate([incontro, info.get("risultato",""), info.get("marcatori","")], 1):
            c = ws.cell(row=i+2, column=col, value=val)
            c.fill = f_alt[i % 2]
            c.alignment = Alignment(horizontal="left" if col==1 else "center", vertical="center")
            c.border = bordo()
        ws.row_dimensions[i+2].height = 18

    ws.column_dimensions['A'].width = 32
    ws.column_dimensions['B'].width = 14
    ws.column_dimensions['C'].width = 35

    # ── GIRONI ────────────────────────────────────────────────────────────────
    ws_g = wb.create_sheet("GIRONI")
    for col, h in enumerate(["GIRONE", "1° CLASSIFICATA", "2° CLASSIFICATA"], 1):
        c = ws_g.cell(row=1, column=col, value=h)
        c.font = h_font; c.fill = h_fill
        c.alignment = h_alg; c.border = bordo()
    ws_g.row_dimensions[1].height = 24

    gir_fill = PatternFill("solid", start_color="EEF2F7")
    for i, (lettera, squadre) in enumerate(GIRONI_SQUADRE.items(), 2):
        info = gironi.get(lettera, {})
        c = ws_g.cell(row=i, column=1, value=lettera)
        c.font = Font(bold=True, size=11, color="1A2E45")
        c.fill = gir_fill; c.alignment = h_alg; c.border = bordo()

        formula = '"' + ','.join(squadre) + '"'
        for col, val in [(2, info.get("prima","")), (3, info.get("seconda",""))]:
            cell = ws_g.cell(row=i, column=col, value=val)
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.border = bordo()
            dv = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
            ws_g.add_data_validation(dv)
            dv.add(cell)
        ws_g.row_dimensions[i].height = 22

    ws_g.column_dimensions['A'].width = 10
    ws_g.column_dimensions['B'].width = 28
    ws_g.column_dimensions['C'].width = 28

    # ── SPECIALI ──────────────────────────────────────────────────────────────
    ws_s = wb.create_sheet("SPECIALI")
    for col, h in enumerate(["VOCE", "VALORE"], 1):
        c = ws_s.cell(row=1, column=col, value=h)
        c.font = h_font; c.fill = h_fill
        c.alignment = h_alg; c.border = bordo()

    # Leggi valori speciali esistenti dal file attuale (non sovrascriverli)
    speciali_esistenti = {}
    try:
        wb_old = openpyxl.load_workbook(RISULTATI_FILE, data_only=True)
        if "SPECIALI" in wb_old.sheetnames:
            ws_old = wb_old["SPECIALI"]
            for row in ws_old.iter_rows(min_row=2, values_only=True):
                if row[0] and row[1]:
                    speciali_esistenti[str(row[0]).strip()] = str(row[1]).strip()
    except Exception:
        pass

    voci = ["VINCITORE", "FINALISTA 1", "FINALISTA 2", "CAPOCANNONIERE",
            "ASSISTMAN", "MVP TORNEO", "MIGLIOR PORTIERE", "MIGLIOR GIOVANE U21"]
    for i, voce in enumerate(voci, 2):
        valore = speciali_esistenti.get(voce, "")
        for col, val in [(1, voce), (2, valore)]:
            c = ws_s.cell(row=i, column=col, value=val)
            c.fill = f_alt[i % 2]
            c.alignment = Alignment(horizontal="left", vertical="center")
            c.border = bordo()
        ws_s.row_dimensions[i].height = 20

    ws_s.column_dimensions['A'].width = 25
    ws_s.column_dimensions['B'].width = 25
    ws_s.row_dimensions[1].height = 24

    RISULTATI_FILE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(RISULTATI_FILE)
    log.info(f"risultati.xlsx aggiornato: {RISULTATI_FILE}")


def salva_storico_posizioni(punteggi, storico_path: Path) -> None:
    """Salva le posizioni correnti in JSON prima di aggiornare."""
    storico_path.parent.mkdir(parents=True, exist_ok=True)
    posizioni = {p.nome_completo: idx + 1 for idx, p in enumerate(punteggi)}
    try:
        with open(storico_path, "w", encoding="utf-8") as f:
            json.dump(posizioni, f, ensure_ascii=False, indent=2)
        log.info(f"Storico posizioni salvato: {storico_path}")
    except Exception as e:
        log.error(f"Errore salvataggio storico: {e}")


def main():
    if not API_KEY:
        log.error("API_FOOTBALL_KEY non trovata nelle variabili d'ambiente!")
        sys.exit(1)

    log.info("=== Avvio aggiornamento automatico ===")

    # 1. Scarica risultati reali
    partite = scarica_risultati()
    gironi  = scarica_gironi()

    # 2. Scrivi risultati.xlsx SOLO se l'API ha restituito dati reali
    # Se partite == 0 significa che il Mondiale non è iniziato o l'API non funziona
    # In questo caso NON sovrascrivere il file risultati inserito manualmente
    if len(partite) > 0:
        scrivi_risultati(partite, gironi)
        log.info(f"risultati.xlsx aggiornato con {len(partite)} partite dall'API")
    else:
        log.info("API ha restituito 0 partite — risultati.xlsx NON modificato (preservo dati manuali)")

    # 3. Leggi pronostici partecipanti
    from src.config import PRONOSTICI_DIR
    partecipanti = leggi_tutti_pronostici(PRONOSTICI_DIR)
    if not partecipanti:
        log.warning("Nessun partecipante trovato!")
        return

    # 4. Calcola punteggi
    risultati = leggi_risultati(RISULTATI_FILE)
    punteggi  = calcola_tutti_punteggi(partecipanti, risultati)

    # 5. Salva storico posizioni e genera output
    storico_path = Path(__file__).parent / "data" / "storico_posizioni.json"
    salva_storico_posizioni(punteggi, storico_path)
    genera_excel_classifica(punteggi)
    genera_html(
        punteggi,
        n_partite_giocate=len(partite),
        partecipanti=partecipanti,
        risultati=risultati,
        storico_path=storico_path,
    )

    log.info(f"=== Completato: {len(punteggi)} partecipanti, {len(partite)} partite ===")
    print(f"\n✅ Classifica aggiornata: {len(punteggi)} partecipanti | {len(partite)} partite giocate")


if __name__ == "__main__":
    main()
