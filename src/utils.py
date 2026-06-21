"""
utils.py - Funzioni di utilità condivise
"""
import re
import unicodedata
from typing import Optional
from datetime import datetime


def normalizza_stringa(s: Optional[str]) -> str:
    """
    Normalizza una stringa per il confronto:
    - strip spazi
    - lowercase
    - rimuovi accenti
    - compatta spazi multipli
    """
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    # Rimuovi spazi iniziali/finali
    s = s.strip()
    # Compatta spazi multipli
    s = re.sub(r"\s+", " ", s)
    # Normalizza accenti (NFKD + rimozione combining chars)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def normalizza_squadra(nome: Optional[str]) -> str:
    """Normalizza il nome di una squadra mantenendo la forma originale ma pulita."""
    if nome is None:
        return ""
    if not isinstance(nome, str):
        nome = str(nome)
    nome = nome.strip()
    nome = re.sub(r"\s+", " ", nome)
    return nome


def confronta_squadre(a: Optional[str], b: Optional[str]) -> bool:
    """
    Confronto intelligente tra due nomi (squadre o giocatori).

    Gestisce i casi:
    - Confronto esatto normalizzato:      "Kane" == "Kane"
    - Match parziale cognome:             "Kane" in "Harry Kane"
    - Accenti e maiuscole ignorate:       "Mbappe" == "Mbappé"
    - Abbreviazioni con punto:            "H. Kane" ~ "Harry Kane"
    - Nome puntato + cognome:             "J.David" ~ "Jonathan David" ~ "David"
    - Sottostringa fuzzy:                 "Rapinha" ~ "Raphinha"
    - Alias comuni:                       "Vini Jr" ~ "Vinicius Junior"
    """
    na = normalizza_stringa(a)
    nb = normalizza_stringa(b)

    if not na or not nb:
        return False

    # ── 1. Confronto esatto ───────────────────────────────────────────────────
    if na == nb:
        return True

    # ── 2. Match parziale contenimento ───────────────────────────────────────
    # Evita false corrispondenze tipo "Gimenez" in "Jimenez"
    # Solo se la parola principale inizia con la stessa lettera
    if na in nb and len(na) >= 4:
        # Verifica che non sia solo una sottostringa casuale
        # es. "son" in "person" → False, "jimenez" in "r. jimenez" → True
        # Minimo 4 caratteri per evitare "ito" in "mitoma"
        idx = nb.index(na)
        if idx == 0 or nb[idx-1] in (' ', '.', '-'):
            return True
    if nb in na and len(nb) >= 4:
        idx = na.index(nb)
        if idx == 0 or na[idx-1] in (' ', '.', '-'):
            return True

    # ── 3. Nome puntato: "j.david" → "david" oppure "jonathan david" ─────────
    # Rimuovi iniziali tipo "j." "r." all'inizio o in mezzo
    def rimuovi_iniziali(s: str) -> str:
        parole = s.split()
        return " ".join(p for p in parole if not re.fullmatch(r"[a-z]\.", p))

    # Gestisci anche "j.david" senza spazio → "david"
    def espandi_nome_puntato(s: str) -> str:
        # "j.david" → "david", "r.lewandowski" → "lewandowski"
        return re.sub(r"^[a-z]\.", "", s).strip()

    na2 = rimuovi_iniziali(na)
    nb2 = rimuovi_iniziali(nb)
    na3 = espandi_nome_puntato(na)
    nb3 = espandi_nome_puntato(nb)

    if na2 and nb2:
        if na2 == nb2:
            return True
        # Minimo 4 caratteri per evitare "ito" in "mitoma"
        if len(na2) >= 4 and len(nb2) >= 4 and (na2 in nb2 or nb2 in na2):
            return True
    if na3 and nb3:
        if na3 == nb3:
            return True
        if len(na3) >= 4 and len(nb3) >= 4 and (na3 in nb3 or nb3 in na3):
            return True
    if na3 and nb2 and len(na3) >= 4 and len(nb2) >= 4 and (na3 in nb2 or nb2 in na3):
        return True
    if nb3 and na2 and len(nb3) >= 4 and len(na2) >= 4 and (nb3 in na2 or na2 in nb3):
        return True

    # ── 4. Parole significative condivise ─────────────────────────────────────
    # Es. "De Bruyne" vs "Kevin De Bruyne" → parola "de bruyne" in comune
    parole_a = {p for p in na2.split() if len(p) > 2}
    parole_b = {p for p in nb2.split() if len(p) > 2}
    if parole_a and parole_b:
        comuni = parole_a & parole_b
        if comuni and (len(parole_a) == 1 or len(parole_b) == 1):
            return True
        # Tutte le parole di uno sono nell'altro
        if parole_a.issubset(parole_b) or parole_b.issubset(parole_a):
            return True

    # ── 5. Similarità fuzzy per errori di battitura ───────────────────────────
    # Es. "rapinha" vs "raphinha", "vinicius" vs "vini"
    # Usa distanza di Levenshtein semplificata
    def distanza_levenshtein(s1: str, s2: str) -> int:
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        distanze = range(len(s1) + 1)
        for c2 in s2:
            nuove = [distanze[0] + 1]
            for c1, d in zip(s1, distanze):
                nuove.append(min(d + (c1 != c2), nuove[-1] + 1, distanze[len(nuove)] + 1))
            distanze = nuove
        return distanze[-1]

    # Confronta le parole più lunghe dei due nomi (probabile cognome)
    def parola_principale(s: str) -> str:
        parole = [p for p in s.split() if len(p) > 3]
        return max(parole, key=len) if parole else s

    pp_a = parola_principale(na)
    pp_b = parola_principale(nb)

    # ── 6. Alias e soprannomi comuni (PRIMA del fuzzy per evitare return False anticipato) ──
    ALIAS = {
        "vini jr":        ["vinicius junior", "vinicius", "vini", "junior", "v. junior"],
        "vini":           ["vinicius junior", "vinicius", "junior", "v. junior"],
        "vinicius":       ["vinicius junior", "vini jr", "vini", "junior", "v. junior"],
        "raphinha":       ["rapinha", "raphinha"],
        "rapinha":        ["raphinha"],
        "neymar":         ["neymar jr"],
        "neymar jr":      ["neymar"],
        "ronaldo":        ["cristiano ronaldo", "cr7"],
        "cr7":            ["cristiano ronaldo", "ronaldo"],
        "messi":          ["lionel messi", "leo messi"],
        "leo messi":      ["messi", "lionel messi"],
        "mbappe":         ["kylian mbappe", "kylian mbape"],
        "son":            ["heung-min son", "heung min son"],
        "benzema":        ["karim benzema"],
        "salah":          ["mohamed salah"],
        "firmino":        ["roberto firmino"],
        "luiz diaz":      ["luis diaz"],
        "luis diaz":      ["luiz diaz"],
    }

    for alias_key, alias_vals in ALIAS.items():
        if na == alias_key and nb in alias_vals:
            return True
        if nb == alias_key and na in alias_vals:
            return True
        if na in alias_vals and nb == alias_key:
            return True
        if nb in alias_vals and na == alias_key:
            return True

    # ── 7. Fuzzy per errori di battitura ──────────────────────────────────────
    if pp_a and pp_b:
        # La prima lettera deve coincidere per evitare false corrispondenze
        if pp_a[0] != pp_b[0]:
            return False
        lunghezza_max = max(len(pp_a), len(pp_b))
        dist = distanza_levenshtein(pp_a, pp_b)
        if lunghezza_max <= 8 and dist <= 1:
            return True
        elif lunghezza_max > 10 and dist <= 2:
            return True

    return False


def normalizza_risultato(risultato: Optional[str]) -> Optional[str]:
    """
    Normalizza un risultato tipo "2 - 1", "2-1 ", "2:1" → "2-1"
    Ritorna None se non valido.
    """
    if not risultato:
        return None
    if not isinstance(risultato, str):
        risultato = str(risultato)
    # Sostituisci separatori alternativi
    r = re.sub(r"[\s:–—]", "-", risultato.strip())
    # Rimuovi spazi attorno al trattino
    r = re.sub(r"\s*-\s*", "-", r)
    # Verifica formato N-N
    if re.fullmatch(r"\d+-\d+", r):
        return r
    return None


def normalizza_esito(esito: Optional[str]) -> Optional[str]:
    """Normalizza esito: accetta '1','X','x','2' → '1','X','2'"""
    if not esito:
        return None
    e = str(esito).strip().upper()
    if e in ("1", "X", "2"):
        return e
    return None


def estrai_goller(risultato: Optional[str]) -> tuple[int, int]:
    """Estrae (gol_casa, gol_ospite) da un risultato normalizzato."""
    if not risultato:
        return (0, 0)
    try:
        parti = risultato.split("-")
        return int(parti[0]), int(parti[1])
    except (ValueError, IndexError):
        return (0, 0)


def calcola_esito_da_risultato(risultato: Optional[str]) -> Optional[str]:
    """Calcola l'esito 1/X/2 da un risultato 'N-N'."""
    r = normalizza_risultato(risultato)
    if not r:
        return None
    g1, g2 = estrai_goller(r)
    if g1 > g2:
        return "1"
    elif g1 == g2:
        return "X"
    else:
        return "2"


def timestamp_ora() -> str:
    """Restituisce il timestamp attuale formattato in ora italiana (UTC+2)."""
    from datetime import timezone, timedelta
    tz_italia = timezone(timedelta(hours=2))  # CEST (ora legale italiana)
    return datetime.now(tz=tz_italia).strftime("%d/%m/%Y %H:%M:%S")


def safe_str(val) -> str:
    """Converte qualsiasi valore in stringa sicura, None → ''."""
    if val is None:
        return ""
    if isinstance(val, float) and val != val:  # NaN check
        return ""
    return str(val).strip()


# Dizionario bandiere per paese
BANDIERE = {
    "messico": "🇲🇽", "sud africa": "🇿🇦", "corea del sud": "🇰🇷",
    "repubblica ceca": "🇨🇿", "r.ceca": "🇨🇿", "canada": "🇨🇦",
    "bosnia": "🇧🇦", "bosnia erzegovina": "🇧🇦", "qatar": "🇶🇦",
    "svizzera": "🇨🇭", "brasile": "🇧🇷", "marocco": "🇲🇦",
    "haiti": "🇭🇹", "scozia": "🏴", "usa": "🇺🇸",
    "paraguay": "🇵🇾", "australia": "🇦🇺", "turchia": "🇹🇷",
    "germania": "🇩🇪", "curacao": "🇨🇼", "costa d'avorio": "🇨🇮",
    "ecuador": "🇪🇨", "olanda": "🇳🇱", "giappone": "🇯🇵",
    "svezia": "🇸🇪", "tunisia": "🇹🇳", "spagna": "🇪🇸",
    "capo verde": "🇨🇻", "arabia saudita": "🇸🇦", "uruguay": "🇺🇾",
    "belgio": "🇧🇪", "egitto": "🇪🇬", "iran": "🇮🇷",
    "nuova zelanda": "🇳🇿", "francia": "🇫🇷", "senegal": "🇸🇳",
    "iraq": "🇮🇶", "norvegia": "🇳🇴", "argentina": "🇦🇷",
    "algeria": "🇩🇿", "austria": "🇦🇹", "giordania": "🇯🇴",
    "portogallo": "🇵🇹", "congo": "🇨🇩", "uzbekistan": "🇺🇿",
    "colombia": "🇨🇴", "inghilterra": "🏴", "croazia": "🇭🇷",
    "ghana": "🇬🇭", "panama": "🇵🇦",
}


def bandiera(nome_squadra: str) -> str:
    """Restituisce la bandiera emoji per una squadra."""
    if not nome_squadra:
        return ""
    key = normalizza_stringa(nome_squadra)
    return BANDIERE.get(key, "🏳️")
