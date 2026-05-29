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
    """Confronto case-insensitive e accent-insensitive tra due nomi squadra."""
    return normalizza_stringa(a) == normalizza_stringa(b)


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
    """Restituisce il timestamp attuale formattato."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def safe_str(val) -> str:
    """Converte qualsiasi valore in stringa sicura, None → ''."""
    if val is None:
        return ""
    if isinstance(val, float) and val != val:  # NaN check
        return ""
    return str(val).strip()
