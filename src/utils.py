"""
utils.py - Funzioni di utilità condivise
"""
import re
import unicodedata
from typing import Optional
from datetime import datetime


def normalizza_stringa(s: Optional[str]) -> str:
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def normalizza_squadra(nome: Optional[str]) -> str:
    if nome is None:
        return ""
    if not isinstance(nome, str):
        nome = str(nome)
    nome = nome.strip()
    nome = re.sub(r"\s+", " ", nome)
    return nome


def confronta_squadre(a: Optional[str], b: Optional[str]) -> bool:
    na = normalizza_stringa(a)
    nb = normalizza_stringa(b)

    if not na or not nb:
        return False

    if na == nb:
        return True

    if na in nb and len(na) >= 4:
        idx = nb.index(na)
        if idx == 0 or nb[idx-1] in (' ', '.', '-'):
            return True
    if nb in na and len(nb) >= 4:
        idx = na.index(nb)
        if idx == 0 or na[idx-1] in (' ', '.', '-'):
            return True

    def rimuovi_iniziali(s: str) -> str:
        parole = s.split()
        return " ".join(p for p in parole if not re.fullmatch(r"[a-z]\.", p))

    def espandi_nome_puntato(s: str) -> str:
        return re.sub(r"^[a-z]\.", "", s).strip()

    na2 = rimuovi_iniziali(na)
    nb2 = rimuovi_iniziali(nb)
    na3 = espandi_nome_puntato(na)
    nb3 = espandi_nome_puntato(nb)

    if na2 and nb2:
        if na2 == nb2:
            return True
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

    parole_a = {p for p in na2.split() if len(p) > 2}
    parole_b = {p for p in nb2.split() if len(p) > 2}
    if parole_a and parole_b:
        comuni = parole_a & parole_b
        if comuni and (len(parole_a) == 1 or len(parole_b) == 1):
            return True
        if parole_a.issubset(parole_b) or parole_b.issubset(parole_a):
            return True

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

    def parola_principale(s: str) -> str:
        parole = [p for p in s.split() if len(p) > 3]
        return max(parole, key=len) if parole else s

    pp_a = parola_principale(na)
    pp_b = parola_principale(nb)

    # ── 6. Alias e soprannomi comuni ─────────────────────────────────────────
    ALIAS = {
        # Giocatori
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
        # Nazioni italiano ↔ inglese
        "brasile":        ["brazil", "brasil"],
        "brazil":         ["brasile", "brasil"],
        "brasil":         ["brasile", "brazil"],
        "inghilterra":    ["england"],
        "england":        ["inghilterra"],
        "germania":       ["germany"],
        "germany":        ["germania"],
        "francia":        ["france"],
        "france":         ["francia"],
        "spagna":         ["spain"],
        "spain":          ["spagna"],
        "olanda":         ["netherlands", "holland"],
        "netherlands":    ["olanda", "holland"],
        "holland":        ["olanda", "netherlands"],
        "belgio":         ["belgium"],
        "belgium":        ["belgio"],
        "portogallo":     ["portugal"],
        "portugal":       ["portogallo"],
        "svizzera":       ["switzerland"],
        "switzerland":    ["svizzera"],
        "norvegia":       ["norway"],
        "norway":         ["norvegia"],
        "svezia":         ["sweden"],
        "sweden":         ["svezia"],
        "giappone":       ["japan"],
        "japan":          ["giappone"],
        "messico":        ["mexico"],
        "mexico":         ["messico"],
        "marocco":        ["morocco"],
        "morocco":        ["marocco"],
        "croazia":        ["croatia"],
        "croatia":        ["croazia"],
        "senegal":        ["senegal"],
        "egitto":         ["egypt"],
        "egypt":          ["egitto"],
        "nuova zelanda":  ["new zealand"],
        "new zealand":    ["nuova zelanda"],
        "arabia saudita": ["saudi arabia", "ksa"],
        "saudi arabia":   ["arabia saudita"],
        "ksa":            ["arabia saudita"],
        "capo verde":     ["cape verde", "cabo verde"],
        "cape verde":     ["capo verde"],
        "cabo verde":     ["capo verde"],
        "corea del sud":  ["korea republic", "south korea"],
        "korea republic": ["corea del sud"],
        "south korea":    ["corea del sud"],
        "costa d'avorio": ["ivory coast", "cote d'ivoire"],
        "ivory coast":    ["costa d'avorio"],
        "sud africa":     ["south africa"],
        "south africa":   ["sud africa"],
        "r.ceca":         ["czech republic", "czechia"],
        "czech republic": ["r.ceca"],
        "czechia":        ["r.ceca"],
        "bosnia":         ["bosnia and herzegovina", "bosnia-herzegovina"],
        "bosnia and herzegovina": ["bosnia"],
        "bosnia-herzegovina":     ["bosnia"],
        "dr congo":       ["congo", "democratic republic of the congo"],
        "congo":          ["dr congo"],
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
    if not risultato:
        return None
    if not isinstance(risultato, str):
        risultato = str(risultato)
    r = re.sub(r"[\s:–—]", "-", risultato.strip())
    r = re.sub(r"\s*-\s*", "-", r)
    if re.fullmatch(r"\d+-\d+", r):
        return r
    return None


def normalizza_esito(esito: Optional[str]) -> Optional[str]:
    if not esito:
        return None
    e = str(esito).strip().upper()
    if e in ("1", "X", "2"):
        return e
    return None


def estrai_goller(risultato: Optional[str]) -> tuple[int, int]:
    if not risultato:
        return (0, 0)
    try:
        parti = risultato.split("-")
        return int(parti[0]), int(parti[1])
    except (ValueError, IndexError):
        return (0, 0)


def calcola_esito_da_risultato(risultato: Optional[str]) -> Optional[str]:
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
    from datetime import timezone, timedelta
    tz_italia = timezone(timedelta(hours=2))
    return datetime.now(tz=tz_italia).strftime("%d/%m/%Y %H:%M:%S")


def safe_str(val) -> str:
    if val is None:
        return ""
    if isinstance(val, float) and val != val:
        return ""
    return str(val).strip()


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
    if not nome_squadra:
        return ""
    key = normalizza_stringa(nome_squadra)
    return BANDIERE.get(key, "🏳️")
