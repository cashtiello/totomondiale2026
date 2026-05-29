# 🏆 TotoMondiale 2026 – Manager Automatico

Sistema completo per la gestione automatica del Totomondiale 2026.

---

## 🚀 Avvio Rapido (Windows)

1. **Doppio clic** su `run.bat`

Il programma:
- Installa automaticamente le dipendenze Python
- Legge tutti i file pronostici
- Calcola i punteggi
- Genera la classifica Excel e HTML
- Apre la classifica nel browser

---

## 📋 Prerequisiti

- **Python 3.12+** → [python.org](https://python.org)
- Connessione Internet (solo per la prima installazione delle librerie)

---

## 📁 Struttura del Progetto

```
totomondiale/
│
├── data/
│   ├── pronostici/              ← INSERISCI QUI i file .xlsx dei partecipanti
│   ├── risultati_reali/
│   │   └── risultati.xlsx       ← COMPILA con i risultati reali
│   ├── output/
│   │   ├── classifica.xlsx      ← Generato automaticamente
│   │   └── index.html           ← Generato automaticamente (apri nel browser)
│   └── logs/
│       └── totomondiale.log
│
├── templates/
│   └── classifica.html          ← Template HTML (non modificare)
│
├── src/
│   ├── main.py                  ← Entry point
│   ├── config.py                ← Configurazione e punteggi
│   ├── models.py                ← Strutture dati
│   ├── excel_reader.py          ← Lettura file partecipanti
│   ├── parser_pronostici.py     ← Parser file Excel partecipanti
│   ├── parser_risultati.py      ← Parser file risultati reali
│   ├── calcolo_punti.py         ← Logica di calcolo punteggi
│   ├── generatore_classifica.py ← Generazione Excel classifica
│   ├── html_generator.py        ← Generazione pagina HTML
│   ├── utils.py                 ← Funzioni di utilità
│   └── logger.py                ← Configurazione logging
│
├── requirements.txt
├── README.md
└── run.bat                      ← Avvio su Windows
```

---

## 📂 Come Aggiungere i Partecipanti

1. Ogni partecipante compila il file Excel **TOTOMONDIALE2026.xlsx**
2. Salva il file con un nome qualsiasi (es. `MarioRossi.xlsx`)
3. **Copia** il file nella cartella `data/pronostici/`
4. Lancia `run.bat`

Il sistema leggerà **automaticamente** tutti i file `.xlsx` presenti nella cartella.

---

## 📋 Inserimento Risultati Reali

Apri il file `data/risultati_reali/risultati.xlsx` (creato automaticamente al primo avvio).

### Foglio PARTITE
| PARTITA | RISULTATO | MARCATORE |
|---------|-----------|-----------|
| Messico-Sud Africa | 1-0 | Gimenez |
| Corea del Sud-R.Ceca | 2-1 | Son |

- **PARTITA**: nome identico a come appare nel file pronostici (es. `Messico-Sud Africa`)
- **RISULTATO**: formato `N-N` (es. `1-0`, `2-2`)
- **MARCATORE**: cognome del marcatore (lascia vuoto se non previsto)

### Foglio GIRONI
| GIRONE | 1° CLASSIFICATA | 2° CLASSIFICATA |
|--------|-----------------|-----------------|
| A | Messico | Corea del Sud |
| B | Canada | Svizzera |

### Foglio SPECIALI
| VOCE | VALORE |
|------|--------|
| VINCITORE | Brasile |
| FINALISTA 1 | Argentina |
| FINALISTA 2 | Brasile |
| CAPOCANNONIERE | Vinicius Jr |
| ASSISTMAN | Pedri |
| MVP TORNEO | Vinicius Jr |
| MIGLIOR PORTIERE | Donnarumma |
| MIGLIOR GIOVANE U21 | Yamal |

---

## 🏆 Regolamento Punteggi

### Partite
| Pronostico | Punti |
|-----------|-------|
| Esito 1X2 corretto | 1 pt |
| Risultato esatto | 5 pt (+ 1 pt esito automatico = **6 pt**) |
| Risultato esatto + Marcatore | 5 + 1 + 2 = **8 pt** |
| Marcatore corretto | 2 pt |

> ⚠️ Il risultato esatto include automaticamente il punto per l'esito.

### Gironi
| Pronostico | Punti |
|-----------|-------|
| Accoppiata esatta (ordine corretto) | 6 pt |
| Accoppiata giusta (ordine errato) | 4 pt |
| Singola squadra qualificata | 1 pt per squadra |

### Sezioni Speciali
| Pronostico | Punti |
|-----------|-------|
| Vincitore Competizione | 20 pt |
| Finale Esatta (entrambe) | 15 pt |
| Finalista Singola | 10 pt |
| Capocannoniere | 10 pt |
| Assistman | 12 pt |
| MVP Torneo | 10 pt |
| Miglior Portiere | 10 pt |
| Miglior Giovane U21 | 15 pt |

---

## ⚙️ Avvio da Terminale

```bash
# Installa dipendenze (una volta sola)
pip install -r requirements.txt

# Avvia il programma
python src/main.py
```

---

## 🛠️ Personalizzazione

### Modifica i punteggi
Apri `src/config.py` e modifica i valori nella sezione `# Punteggi`.

### Aggiungere nuovi partecipanti
Basta copiare il file nella cartella `data/pronostici/` e rieseguire il programma.

### Log di debug
Apri `data/logs/totomondiale.log` per vedere i dettagli di ogni elaborazione.

---

## 🐛 Risoluzione Problemi

| Problema | Soluzione |
|---------|-----------|
| "Python non trovato" | Installa Python 3.12+ da python.org e aggiungi al PATH |
| File non caricato | Controlla il log → `data/logs/totomondiale.log` |
| Punteggi errati | Verifica nomi squadre in `risultati.xlsx` (devono corrispondere) |
| Pagina HTML non si apre | Apri manualmente `data/output/index.html` nel browser |

---

## 📊 Output Generato

- **`data/output/classifica.xlsx`**: 3 fogli (Classifica, Statistiche, Dettaglio)
- **`data/output/index.html`**: Pagina web con classifica interattiva, podio, record
- **`data/logs/totomondiale.log`**: Log completo dell'elaborazione

---

*TotoMondiale 2026 Manager – Sviluppato con Python 3.12*
