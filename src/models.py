"""
models.py - Dataclasses per tutti gli oggetti del dominio Totomondiale 2026
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Partita:
    """Rappresenta una partita del tabellone."""
    data: Optional[datetime]
    gruppo: str
    incontro: str       # es. "Messico-Sud Africa"
    squadra_casa: str
    squadra_ospite: str


@dataclass
class PronosticoPartita:
    """Pronostico di un partecipante per una singola partita."""
    incontro: str
    esito: Optional[str]         # "1", "X", "2"
    risultato_esatto: Optional[str]  # es. "2-1"
    marcatore: Optional[str]


@dataclass
class PronosticoGirone:
    """Pronostico per il passaggio del turno di un girone."""
    girone: str                  # "A", "B", ..., "L"
    prima: Optional[str]         # 1° classificata
    seconda: Optional[str]       # 2° classificata


@dataclass
class PronosticoSpeciale:
    """Pronostici speciali (finale, vincitore, premi individuali)."""
    vincitore: Optional[str] = None
    finalista_1: Optional[str] = None
    finalista_2: Optional[str] = None
    capocannoniere: Optional[str] = None
    assistman: Optional[str] = None
    mvp: Optional[str] = None
    miglior_portiere: Optional[str] = None
    miglior_giovane: Optional[str] = None


@dataclass
class PronosticoPartecipante:
    """Tutti i pronostici di un singolo partecipante."""
    nome: str
    cognome: str
    file_sorgente: str
    partite: list[PronosticoPartita] = field(default_factory=list)
    gironi: list[PronosticoGirone] = field(default_factory=list)
    speciali: PronosticoSpeciale = field(default_factory=PronosticoSpeciale)

    @property
    def nome_completo(self) -> str:
        parts = [self.nome, self.cognome]
        return " ".join(p for p in parts if p).strip() or "Sconosciuto"


@dataclass
class RisultatoPartita:
    """Risultato reale di una partita inserito dall'amministratore."""
    incontro: str
    risultato: Optional[str]     # es. "1-0"
    marcatore: Optional[str]

    @property
    def esito(self) -> Optional[str]:
        """Deriva l'esito 1X2 dal risultato."""
        if not self.risultato:
            return None
        try:
            parti = self.risultato.replace(" ", "").split("-")
            if len(parti) != 2:
                return None
            g1, g2 = int(parti[0]), int(parti[1])
            if g1 > g2:
                return "1"
            elif g1 == g2:
                return "X"
            else:
                return "2"
        except (ValueError, IndexError):
            return None


@dataclass
class RisultatoGirone:
    """Risultato reale per la classifica di un girone."""
    girone: str
    prima: Optional[str]
    seconda: Optional[str]


@dataclass
class RisultatiReali:
    """Contenitore di tutti i risultati reali."""
    partite: dict[str, RisultatoPartita] = field(default_factory=dict)
    gironi: dict[str, RisultatoGirone] = field(default_factory=dict)
    vincitore: Optional[str] = None
    finalista_1: Optional[str] = None
    finalista_2: Optional[str] = None
    capocannoniere: Optional[str] = None
    assistman: Optional[str] = None
    mvp: Optional[str] = None
    miglior_portiere: Optional[str] = None
    miglior_giovane: Optional[str] = None


@dataclass
class PunteggioDettaglio:
    """Dettaglio punteggio per un partecipante."""
    nome_completo: str
    nome: str
    cognome: str
    file_sorgente: str

    # Punti partite
    pt_esito: int = 0
    pt_risultato_esatto: int = 0
    pt_marcatore: int = 0

    # Punti gironi
    pt_gironi: int = 0

    # Punti speciali
    pt_vincitore: int = 0
    pt_finalista: int = 0
    pt_capocannoniere: int = 0
    pt_assistman: int = 0
    pt_mvp: int = 0
    pt_miglior_portiere: int = 0
    pt_miglior_giovane: int = 0

    # Contatori statistici
    n_esiti_corretti: int = 0
    n_risultati_esatti: int = 0
    n_marcatori_corretti: int = 0
    n_gironi_coppia_esatta: int = 0
    n_gironi_coppia_invertita: int = 0
    n_gironi_singola: int = 0

    @property
    def punti_totali(self) -> int:
        return (
            self.pt_esito + self.pt_risultato_esatto + self.pt_marcatore
            + self.pt_gironi
            + self.pt_vincitore + self.pt_finalista
            + self.pt_capocannoniere + self.pt_assistman
            + self.pt_mvp + self.pt_miglior_portiere + self.pt_miglior_giovane
        )

    @property
    def punti_partite(self) -> int:
        return self.pt_esito + self.pt_risultato_esatto + self.pt_marcatore

    @property
    def punti_speciali(self) -> int:
        return (
            self.pt_vincitore + self.pt_finalista
            + self.pt_capocannoniere + self.pt_assistman
            + self.pt_mvp + self.pt_miglior_portiere + self.pt_miglior_giovane
        )
